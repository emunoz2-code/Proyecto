"""HC-SR04: ECHO debe pasar por divisor resistivo antes de GPIO34."""
from machine import Pin, time_pulse_us
from time import sleep_us


class Ultrasonic:
    def __init__(self, cfg):
        self.trig = Pin(cfg.TRIG, Pin.OUT, value=0)
        self.echo = Pin(cfg.ECHO, Pin.IN)
        self.timeout = cfg.ECHO_TIMEOUT_US

    def read_cm(self):
        self.trig.value(0)
        sleep_us(2)
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)
        try:
            duration = time_pulse_us(self.echo, 1, self.timeout)
        except OSError:
            return None
        # MicroPython devuelve -2 o -1 en los dos tipos de timeout.
        if duration <= 0:
            return None
        distance = duration / 58.0
        return round(distance, 1) if 2 <= distance <= 400 else None
