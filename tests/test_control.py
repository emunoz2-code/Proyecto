import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "firmware"))
import config
from control import Controller


class FakeMotors:
    def __init__(self):
        self.output = ("stop", 0)

    def stop(self):
        self.output = ("stop", 0)

    def drive(self, direction, speed):
        self.output = (direction, speed)


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.counter = 0
        self.motor = FakeMotors()
        self.c = Controller(self.motor, config, self.token)
        self.c.link(True)
        self.c.sensor(100, 0)

    def token(self):
        self.counter += 1
        return str(self.counter)

    def send(self, action, seq=0, now=0, **fields):
        command = {"v": 1, "action": action, "session": self.c.session, "seq": seq}
        command.update(fields)
        return self.c.command(json.dumps(command), False, now)

    def moving(self):
        self.assertTrue(self.send("arm")["ok"])
        self.assertTrue(self.send("move", 1, direction="forward", speed=30)["ok"])

    def test_startup_is_stopped(self):
        self.assertFalse(self.c.armed)
        self.assertEqual(self.motor.output, ("stop", 0))

    def test_move_requires_arm(self):
        self.assertFalse(self.send("move", direction="forward", speed=30)["ok"])

    def test_four_directions(self):
        self.send("arm")
        for seq, direction in enumerate(("forward", "backward", "left", "right"), 1):
            self.assertTrue(self.send("move", seq, direction=direction, speed=30)["ok"])
            self.assertEqual(self.motor.output, (direction, 30))

    def test_move_timeout_even_with_heartbeat(self):
        self.moving()
        self.c.sensor(100, 500)
        self.assertTrue(self.send("heartbeat", 2, 500)["ok"])
        self.c.tick(600)
        self.assertFalse(self.c.armed)
        self.assertEqual(self.c.reason, "move_timeout")
        self.assertEqual(self.motor.output, ("stop", 0))

    def test_command_after_deadline_cannot_revive(self):
        self.moving()
        old = self.c.session
        self.c.sensor(100, 600)
        result = self.send("move", 2, 600, session=old, direction="forward", speed=30)
        self.assertFalse(result["ok"])
        self.assertFalse(self.c.armed)

    def test_repeated_move_renews_lease(self):
        self.moving()
        for seq, now in enumerate(range(200, 2000, 200), 2):
            self.c.sensor(100, now)
            self.assertTrue(self.send("move", seq, now, direction="forward", speed=30)["ok"])
        self.assertTrue(self.c.armed)

    def test_heartbeat_idle_timeout(self):
        self.send("arm")
        self.c.sensor(100, 1000)
        self.c.tick(1000)
        self.assertEqual(self.c.reason, "control_timeout")

    def test_rejects_retained_arm(self):
        msg = {"v": 1, "action": "arm", "session": self.c.session, "seq": 0}
        self.assertFalse(self.c.command(json.dumps(msg), True, 0)["ok"])
        self.assertFalse(self.c.armed)

    def test_duplicate_sequence_does_not_renew(self):
        self.moving()
        self.c.sensor(100, 500)
        self.assertFalse(self.send("move", 1, 500, direction="forward", speed=30)["ok"])
        self.c.tick(600)
        self.assertEqual(self.c.reason, "move_timeout")

    def test_disconnect_rotates_session_and_stops(self):
        self.moving()
        old = self.c.session
        self.c.link(False)
        self.c.link(True)
        self.assertNotEqual(old, self.c.session)
        self.assertFalse(self.c.armed)
        self.assertFalse(self.send("arm", session=old)["ok"])

    def test_obstacle_and_sensor_failure_stop(self):
        for distance in (20, 5, None):
            self.setUp()
            self.moving()
            self.c.sensor(distance, 100)
            self.c.tick(100)
            self.assertFalse(self.c.armed)
            self.assertEqual(self.motor.output, ("stop", 0))

    def test_stale_sensor_stops(self):
        self.moving()
        self.c.tick(350)
        self.assertEqual(self.c.reason, "sensor_stale")

    def test_sensor_recovery_does_not_resume(self):
        self.moving()
        self.c.sensor(None, 100)
        self.c.tick(100)
        self.c.sensor(100, 200)
        self.c.tick(200)
        self.assertFalse(self.c.armed)

    def test_invalid_payloads_do_not_arm(self):
        for payload in ("{", "[]", "null", '"arm"', '{"v":true,"action":"arm"}', "x" * 385):
            self.assertFalse(self.c.command(payload, False, 0)["ok"])
        self.assertFalse(self.c.armed)

    def test_invalid_speed_type_and_limits(self):
        self.send("arm")
        for speed in (True, -1, 0, 61, 100, "30", None, 30.5):
            self.assertFalse(self.send("move", 1, direction="forward", speed=speed)["ok"])
        self.assertEqual(self.motor.output, ("stop", 0))

    def test_unknown_fields_rejected(self):
        self.assertFalse(self.send("arm", extra="invalid")["ok"])

    def test_physical_emergency_is_latched(self):
        self.moving()
        self.c.physical(True)
        self.assertTrue(self.c.estop)
        self.assertFalse(self.send("clear_estop")["ok"])
        self.c.physical(False)
        self.assertFalse(self.send("arm")["ok"])
        self.assertTrue(self.send("clear_estop")["ok"])
        self.assertFalse(self.c.armed)
        self.assertTrue(self.send("arm")["ok"])

    def test_remote_stop_and_emergency_without_session(self):
        for action in ("stop", "estop"):
            self.setUp()
            self.moving()
            result = self.c.command(json.dumps({"v": 1, "action": action}), False, 20)
            self.assertTrue(result["ok"])
            self.assertFalse(self.c.armed)
            self.assertEqual(self.c.estop, action == "estop")

    def test_snapshot_no_fake_battery(self):
        self.assertIsNone(self.c.snapshot(0)["battery_v"])

    def test_tick_wraparound(self):
        period = 1 << 30
        def diff(a, b):
            return (a - b + period // 2) % period - period // 2
        with patch("clockutil.time.ticks_diff", diff, create=True):
            start = period - 100
            self.c.sensor(100, start)
            self.send("arm", now=start)
            self.send("move", 1, start, direction="forward", speed=30)
            self.c.sensor(100, 499)
            self.c.tick(499)
            self.assertTrue(self.c.armed)
            self.c.tick(500)
            self.assertEqual(self.c.reason, "move_timeout")

    def test_invalid_messages_do_not_extend_timeout(self):
        self.moving()
        self.c.sensor(100, 500)
        self.c.command("{broken", False, 500)
        self.c.tick(600)
        self.assertFalse(self.c.armed)


if __name__ == "__main__":
    unittest.main()
