"""Reglas de seguridad independientes de MQTT y de los periféricos."""
import json
from clockutil import elapsed


class Controller:
    def __init__(self, motors, cfg, token_factory):
        self.motors, self.cfg, self.token_factory = motors, cfg, token_factory
        self.session = token_factory()
        self.seq = -1
        self.connected = False
        self.armed = False
        self.estop = False
        self.physical_pressed = False
        self.direction, self.speed = "stop", 0
        self.reason = "startup"
        self.distance = None
        self.sensor_at = None
        self.last_control = None
        self.last_move = None
        self.motors.detener()

    def rotate_session(self):
        self.session = self.token_factory()
        self.seq = -1

    def disarm(self, reason, force_rotate=False):
        active = self.armed or self.direction != "stop"
        self.motors.detener()
        self.armed = False
        self.direction, self.speed = "stop", 0
        self.reason = reason
        self.last_move = self.last_control = None
        if active or force_rotate:
            self.rotate_session()

    def link(self, connected):
        self.connected = connected
        self.disarm("connected" if connected else "disconnected", True)

    def physical(self, pressed):
        self.physical_pressed = bool(pressed)
        if pressed and not self.estop:
            self.estop = True
            self.disarm("physical_estop", True)

    def sensor(self, distance, now):
        self.distance = distance
        self.sensor_at = now

    def sensor_problem(self, now):
        if (self.sensor_at is None or
                elapsed(now, self.sensor_at) >= self.cfg.SENSOR_STALE_MS):
            return "sensor_stale"
        if self.distance is None:
            return "sensor_invalid"
        if self.distance <= self.cfg.OBSTACLE_CM:
            return "obstacle"
        return None

    def tick(self, now):
        if self.armed:
            if not self.connected:
                self.disarm("disconnected")
            elif self.physical_pressed or self.estop:
                self.disarm("estop")
            elif self.sensor_problem(now):
                self.disarm(self.sensor_problem(now))
            elif self.direction != "stop" and elapsed(now, self.last_move) >= self.cfg.MOVE_TIMEOUT_MS:
                self.disarm("move_timeout")
            elif elapsed(now, self.last_control) >= self.cfg.CONTROL_TIMEOUT_MS:
                self.disarm("control_timeout")

    def command(self, payload, retained, now):
        # Caducar antes de procesar: un mensaje retrasado no revive la sesión.
        self.tick(now)
        cmd = None
        try:
            if retained:
                raise ValueError("retained_rejected")
            if len(payload) > 384:
                raise ValueError("payload_too_large")
            cmd = json.loads(payload)
            if not isinstance(cmd, dict):
                raise ValueError("object_required")
            if type(cmd.get("v")) is not int or cmd["v"] != 1:
                raise ValueError("version_invalid")
            action = cmd.get("action")
            actions = ("arm", "move", "heartbeat", "stop", "estop", "clear_estop")
            if action not in actions:
                raise ValueError("action_invalid")
            allowed = ("v", "action", "session", "seq", "direction", "speed") if action == "move" else ("v", "action", "session", "seq")
            if any(key not in allowed for key in cmd):
                raise ValueError("unknown_field")
            if action in ("stop", "estop"):
                if action == "estop":
                    self.estop = True
                self.disarm(action, True)
                return self.ack(True, action, cmd)
            if cmd.get("session") != self.session:
                raise ValueError("session_invalid")
            seq = cmd.get("seq")
            if type(seq) is not int or not 0 <= seq <= 2147483647 or seq <= self.seq:
                raise ValueError("sequence_invalid")
            if not self.connected:
                raise ValueError("disconnected")
            if action == "clear_estop":
                if self.physical_pressed:
                    raise ValueError("physical_estop_pressed")
                self.estop = False
                self.disarm("estop_cleared", True)
                return self.ack(True, "estop_cleared", cmd)
            if self.estop or self.physical_pressed:
                raise ValueError("estop_latched")
            if action == "arm":
                if self.armed:
                    raise ValueError("already_armed")
                problem = self.sensor_problem(now)
                if problem:
                    raise ValueError(problem)
                self.armed = True
                self.reason = "armed"
            elif action == "move":
                if not self.armed:
                    raise ValueError("not_armed")
                direction, speed = cmd.get("direction"), cmd.get("speed")
                if direction not in ("forward", "backward", "left", "right"):
                    raise ValueError("direction_invalid")
                if type(speed) is not int or not 1 <= speed <= self.cfg.MAX_SPEED:
                    raise ValueError("speed_invalid")
                nombres = {"forward": "avanzar", "backward": "retroceder",
                           "left": "izquierda", "right": "derecha"}
                self.motors.aplicar(nombres[direction], speed)
                self.direction, self.speed = direction, speed
                self.last_move = now
                self.reason = "moving"
            elif action == "heartbeat" and not self.armed:
                raise ValueError("not_armed")
            self.seq = seq
            self.last_control = now
            return self.ack(True, action, cmd)
        except (ValueError, TypeError, KeyError) as exc:
            return self.ack(False, str(exc), cmd)

    def ack(self, ok, reason, cmd):
        return {"v": 1, "ok": ok, "reason": reason,
                "seq": cmd.get("seq") if isinstance(cmd, dict) else None,
                "session": self.session}

    def snapshot(self, now):
        return {"v": 1, "session": self.session, "seq": self.seq,
                "uptime_ms": now, "connected": self.connected,
                "armed": self.armed, "estop": self.estop,
                "physical_estop": self.physical_pressed,
                "direction": self.direction, "speed_pct": self.speed,
                "distance_cm": self.distance,
                "sensor_ok": self.sensor_at is not None and self.distance is not None and elapsed(now, self.sensor_at) < self.cfg.SENSOR_STALE_MS,
                "reason": self.reason}
