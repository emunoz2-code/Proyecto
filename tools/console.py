"""Cliente de ensayo del Parcial 2. Movimiento explícito, corto y sin reanudación."""
import argparse
import getpass
import json
import os
import queue
import threading
import time
import uuid
import paho.mqtt.client as mqtt


class Console:
    def __init__(self, args):
        self.base = args.base.rstrip("/")
        self.session = None
        self.seq = 0
        self.state = {}
        self.received_at = 0
        self.lock = threading.Lock()
        self.acks = queue.Queue()
        self.connected = threading.Event()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id="consola-" + uuid.uuid4().hex[:10],
                                  protocol=mqtt.MQTTv311, clean_session=True)
        if args.user:
            password = os.environ.get("MQTT_PASSWORD") or getpass.getpass("Contraseña MQTT: ")
            self.client.username_pw_set(args.user, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(args.host, args.port, keepalive=10)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print("Conexión rechazada:", reason_code)
            return
        client.subscribe([(self.base + "/telemetry", 0),
                          (self.base + "/ack", 0),
                          (self.base + "/availability", 0)])
        self.connected.set()
        print("Conectado. Esperando telemetría actual...")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected.clear()
        with self.lock:
            self.received_at = 0
            self.session = None
        print("Conexión perdida. No se reanudará ningún movimiento.")

    def on_message(self, client, userdata, message):
        try:
            data = json.loads(message.payload)
            if not isinstance(data, dict):
                return
        except (ValueError, UnicodeError):
            return
        if message.topic.endswith("/telemetry"):
            with self.lock:
                if data.get("session") != self.session:
                    self.session = data.get("session")
                    self.seq = 0
                self.state = data
                self.received_at = time.monotonic()
        elif message.topic.endswith("/ack"):
            self.acks.put(data)
        elif not data.get("online", False):
            with self.lock:
                self.received_at = 0
            print("Vehículo fuera de línea (availability).")

    def send(self, action, expected_session=None, **fields):
        if not self.connected.is_set():
            raise RuntimeError("No hay conexión con el broker")
        command = {"v": 1, "action": action}
        with self.lock:
            if action not in ("stop", "estop"):
                if not self.session or time.monotonic() - self.received_at > 1.5:
                    raise RuntimeError("Telemetría ausente o antigua")
                if expected_session is not None and self.session != expected_session:
                    raise RuntimeError("La sesión cambió: movimiento cancelado")
                command.update(session=self.session, seq=self.seq)
                self.seq += 1
        command.update(fields)
        while True:
            try:
                self.acks.get_nowait()
            except queue.Empty:
                break
        result = self.client.publish(self.base + "/cmd", json.dumps(command), qos=0, retain=False)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError("No fue posible enviar la orden")
        if action in ("stop", "estop"):
            return None
        deadline = time.monotonic() + 0.35
        while time.monotonic() < deadline:
            try:
                ack = self.acks.get(timeout=max(0.001, deadline - time.monotonic()))
            except queue.Empty:
                break
            if ack.get("seq") == command["seq"]:
                if action != "clear_estop" and ack.get("session") != command["session"]:
                    raise RuntimeError("La sesión fue invalidada; maniobra cancelada")
                if not ack.get("ok"):
                    raise RuntimeError("ESP32 rechazó la orden: " + str(ack.get("reason")))
                return ack
        raise RuntimeError("Sin confirmación; se cancela la maniobra")

    def move(self, direction, speed, seconds):
        if direction not in ("forward", "backward", "left", "right"):
            raise ValueError("Dirección: forward, backward, left o right")
        if not 1 <= speed <= 60 or not 0 < seconds <= 5:
            raise ValueError("Para esta consola: velocidad 1–60 y duración mayor que 0 hasta 5 s")
        with self.lock:
            session = self.session
        try:
            self.send("arm", expected_session=session)
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                start = time.monotonic()
                self.send("move", expected_session=session, direction=direction, speed=speed)
                time.sleep(max(0, min(0.2 - (time.monotonic() - start), deadline - time.monotonic())))
        finally:
            try:
                self.send("stop")
            except RuntimeError:
                pass  # El timeout local de la placa sigue siendo necesario.

    def close(self):
        if self.connected.is_set():
            info = self.client.publish(self.base + "/cmd", '{"v":1,"action":"stop"}', qos=0, retain=False)
            info.wait_for_publish(timeout=1)
        self.client.disconnect()
        self.client.loop_stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--base", default="prog2/equipo01/carro01")
    parser.add_argument("--user", default="operador", help="Usar cadena vacía solo para simulación pública")
    args = parser.parse_args()
    console = Console(args)
    try:
        if not console.connected.wait(5):
            raise RuntimeError("No se confirmó conexión MQTT")
        print("Órdenes: status | move forward 30 2 | stop | estop | clear | quit")
        print("move arma y mueve durante el tiempo indicado. Usar primero con ruedas elevadas.")
        while True:
            fields = input("> ").split()
            if not fields:
                continue
            try:
                if fields[0] == "quit":
                    break
                if fields[0] == "status":
                    with console.lock:
                        print(json.dumps(console.state, indent=2, ensure_ascii=False))
                elif fields[0] in ("stop", "estop"):
                    console.send(fields[0])
                elif fields[0] == "clear":
                    print(console.send("clear_estop"))
                    print("Esperar nueva telemetría antes de mover.")
                elif fields[0] == "move" and len(fields) == 4:
                    console.move(fields[1], int(fields[2]), float(fields[3]))
                else:
                    print("Orden desconocida")
            except (ValueError, RuntimeError) as exc:
                print(exc)
    except (KeyboardInterrupt, EOFError):
        print("Cierre solicitado")
    finally:
        console.close()


if __name__ == "__main__":
    main()
