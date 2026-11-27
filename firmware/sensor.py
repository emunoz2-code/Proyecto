from machine import Pin, time_pulse_us
from time import sleep_us


class SensorDistancia:
    def __init__(self, trig, echo):
        self.trig = Pin(trig, Pin.OUT, value=0)
        self.echo = Pin(echo, Pin.IN)

    def leer_cm(self):
        self.trig.value(0)
        sleep_us(2)
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)
        try:
            duracion = time_pulse_us(self.echo, 1, 25000)
        except OSError:
            return None
        if duracion <= 0:
            return None
        distancia = duracion / 58.0
        return round(distancia, 1) if 2 <= distancia <= 400 else None
