"""Estado seguro antes de cargar módulos. Requiere resistencias EN a GND."""
from machine import Pin

# Pines del montaje de referencia; actualizar también si se cambia el pinout.
for gpio in (25, 26, 27, 14, 18, 19, 23):
    Pin(gpio, Pin.OUT, value=0)
