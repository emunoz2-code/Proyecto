import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "firmware"))
import config


class PinDouble:
    OUT, IN, PULL_UP = 1, 0, 2

    def __init__(self, pin, mode=None, value=0):
        self.pin, self.level = pin, value

    def value(self, level=None):
        if level is not None:
            self.level = level
        return self.level


class PWMDouble:
    def __init__(self, pin, freq, duty):
        self.pin, self.frequency, self.current = pin, freq, duty

    def duty(self, value):
        self.current = value


def load_adapter(name, machine):
    spec = importlib.util.spec_from_file_location("adapter_" + name, ROOT / "firmware" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"machine": machine}):
        with patch.object(time, "sleep_us", lambda _: None, create=True):
            spec.loader.exec_module(module)
    return module


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.hardware = types.SimpleNamespace(Pin=PinDouble, PWM=PWMDouble, time_pulse_us=lambda *args: 5800)

    def test_initial_enable_zero(self):
        motor = load_adapter("motor", self.hardware).Motors(config)
        self.assertEqual([p.current for p in motor.pwm], [0, 0])
        self.assertEqual([p.level for p in motor.pins], [0, 0, 0, 0])

    def test_pwm_and_direction(self):
        motor = load_adapter("motor", self.hardware).Motors(config)
        motor.drive("forward", 30)
        self.assertEqual([p.current for p in motor.pwm], [306, 306])
        self.assertEqual([p.level for p in motor.pins], [1, 0, 1, 0])
        motor.drive("backward", 30)
        self.assertEqual([p.level for p in motor.pins], [0, 1, 0, 1])
        motor.stop()
        self.assertEqual([p.current for p in motor.pwm], [0, 0])

    def test_motor_invalid_order_stops(self):
        motor = load_adapter("motor", self.hardware).Motors(config)
        motor.drive("forward", 30)
        with self.assertRaises(ValueError):
            motor.drive("forward", 101)
        self.assertEqual([p.current for p in motor.pwm], [0, 0])

    def test_ultrasonic_conversion(self):
        sensor = load_adapter("ultrasonic", self.hardware).Ultrasonic(config)
        self.assertEqual(sensor.read_cm(), 100.0)
        self.assertEqual(sensor.trig.value(), 0)

    def test_ultrasonic_timeouts_and_range(self):
        for duration in (-1, -2, 0, 50, 25000):
            self.hardware.time_pulse_us = lambda *args, d=duration: d
            sensor = load_adapter("ultrasonic", self.hardware).Ultrasonic(config)
            self.assertIsNone(sensor.read_cm())

    def test_ultrasonic_oserror(self):
        def fail(*args):
            raise OSError("sensor unavailable")
        self.hardware.time_pulse_us = fail
        sensor = load_adapter("ultrasonic", self.hardware).Ultrasonic(config)
        self.assertIsNone(sensor.read_cm())


if __name__ == "__main__":
    unittest.main()
