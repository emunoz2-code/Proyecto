"""Salidas al L298N. stop() deshabilita: el vehículo puede seguir por inercia."""
from machine import Pin, PWM
from time import sleep_us


class Motors:
    DIRECTIONS = {
        "forward": (1, 1), "backward": (-1, -1),
        "left": (-1, 1), "right": (1, -1), "stop": (0, 0),
    }

    def __init__(self, cfg):
        self.pins = [Pin(p, Pin.OUT, value=0)
                     for p in (cfg.IN1, cfg.IN2, cfg.IN3, cfg.IN4)]
        # Los EN están en bajo antes de crear el periférico PWM.
        a = Pin(cfg.ENA, Pin.OUT, value=0)
        b = Pin(cfg.ENB, Pin.OUT, value=0)
        self.pwm = [PWM(a, freq=cfg.PWM_HZ, duty=0),
                    PWM(b, freq=cfg.PWM_HZ, duty=0)]
        self.invert = (cfg.INVERT_LEFT, cfg.INVERT_RIGHT)
        self.limit = cfg.MAX_SPEED
        self.signs = (0, 0)
        self.stop()

    def stop(self):
        for pwm in self.pwm:
            pwm.duty(0)
        for pin in self.pins:
            pin.value(0)
        self.signs = (0, 0)

    def drive(self, direction, speed):
        if direction not in self.DIRECTIONS or type(speed) is not int:
            self.stop()
            raise ValueError("Orden de motor inválida")
        if not 0 <= speed <= self.limit:
            self.stop()
            raise ValueError("Velocidad fuera del límite")
        if direction == "stop" or speed == 0:
            self.stop()
            return
        signs = tuple(-v if inv else v for v, inv in
                      zip(self.DIRECTIONS[direction], self.invert))
        if signs != self.signs:
            self.stop()
            sleep_us(100)  # Deshabilitación antes de cambiar dirección.
            for idx, value in enumerate(signs):
                self.pins[idx * 2].value(1 if value > 0 else 0)
                self.pins[idx * 2 + 1].value(1 if value < 0 else 0)
            self.signs = signs
        for pwm in self.pwm:
            pwm.duty(speed * 1023 // 100)
