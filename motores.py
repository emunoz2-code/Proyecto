
from machine import Pin, PWM


class Motores:
    DIRECCIONES = {
        "avanzar": (1, 0, 1, 0),
        "retroceder": (0, 1, 0, 1),
        "izquierda": (0, 1, 1, 0),
        "derecha": (1, 0, 0, 1),
        "detener": (0, 0, 0, 0),
    }

    def __init__(self):
        self.entradas = [Pin(n, Pin.OUT, value=0) for n in (26, 27, 18, 19)]
        self.ena = PWM(Pin(25, Pin.OUT, value=0), freq=1000, duty=0)
        self.enb = PWM(Pin(14, Pin.OUT, value=0), freq=1000, duty=0)
        self.estado = "detener"

    def detener(self):
        self.ena.duty(0)
        self.enb.duty(0)
        for pin in self.entradas:
            pin.value(0)
        self.estado = "detener"

    def aplicar(self, estado, velocidad):
        if estado not in self.DIRECCIONES or not 0 <= velocidad <= 100:
            self.detener()
            raise ValueError("Movimiento o velocidad invalida")
        if estado == "detener" or velocidad == 0:
            self.detener()
            return
        if estado != self.estado:
            self.detener()
            for pin, valor in zip(self.entradas, self.DIRECCIONES[estado]):
                pin.value(valor)
            self.estado = estado
        # MicroPython ESP32: PWM de 0 a 1023 equivale a 0–100 %.
        duty = velocidad * 1023 // 100
        self.ena.duty(duty)
        self.enb.duty(duty)
