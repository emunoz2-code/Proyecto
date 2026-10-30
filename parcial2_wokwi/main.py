"""Parcial 2: vehículo simulado en Wokwi con ESP32 y MicroPython."""
from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff
from motores import Motores
from sensor import SensorDistancia

DISTANCIA_MINIMA = 20  # centímetros


def decidir_estado(estado, orden, distancia):
    """Una nueva pulsación cambia la orden; un obstáculo siempre detiene."""
    if orden is not None:
        estado = orden
    if distancia is None or distancia <= DISTANCIA_MINIMA:
        estado = "detener"
    return estado


def main():
    motores = Motores()
    sensor = SensorDistancia(trig=23, echo=34)
    botones = {
        "avanzar": Pin(32, Pin.IN, Pin.PULL_UP),
        "retroceder": Pin(33, Pin.IN, Pin.PULL_UP),
        "izquierda": Pin(21, Pin.IN, Pin.PULL_UP),
        "derecha": Pin(22, Pin.IN, Pin.PULL_UP),
        "detener": Pin(13, Pin.IN, Pin.PULL_UP),
    }
    potenciometro = ADC(Pin(35))
    potenciometro.atten(ADC.ATTN_11DB)
    potenciometro.width(ADC.WIDTH_12BIT)
    estado = "detener"
    pulsado_anterior = None
    distancia = None
    ultima_lectura = None
    ultimo_reporte = ticks_ms()
    print("PARCIAL 2 - Vehiculo en Wokwi")
    print("Pulse un boton para elegir movimiento; el rojo detiene.")
    print("Potenciometro: potencia de 0 a 100 %. Obstaculo: 20 cm.")

    try:
        while True:
            activos = [nombre for nombre, pin in botones.items() if pin.value() == 0]
            if "detener" in activos or len(activos) > 1:
                pulsado = "detener"
            else:
                pulsado = activos[0] if activos else None
            # Solo una pulsacion nueva permite cambiar de estado.
            orden = pulsado if pulsado != pulsado_anterior else None
            pulsado_anterior = pulsado
            ahora = ticks_ms()
            if ultima_lectura is None or ticks_diff(ahora, ultima_lectura) >= 100:
                distancia = sensor.leer_cm()
                ultima_lectura = ticks_ms()
            estado = decidir_estado(estado, orden, distancia)
            velocidad = potenciometro.read() * 100 // 4095
            if velocidad == 0:
                estado = "detener"
            motores.aplicar(estado, velocidad)

            ahora = ticks_ms()
            if ticks_diff(ahora, ultimo_reporte) >= 500:
                lectura = "sin lectura" if distancia is None else "%.1f cm" % distancia
                potencia = velocidad if estado != "detener" else 0
                print("Distancia: %s | Estado: %s | PWM: %d %%" % (lectura, estado, potencia))
                ultimo_reporte = ahora
            sleep_ms(20)
    finally:
        motores.detener()


if __name__ == "__main__":
    main()
