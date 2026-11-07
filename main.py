
from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff
from motores import Motores
from sensor import SensorDistancia

DISTANCIA_MINIMA = 20  # centimetros
CAMBIO_DISTANCIA_CM = 1.0  # Evita mensajes por variaciones menores de medida.


def decidir_estado(estado, orden, distancia):
    """Una nueva pulsacion cambia la orden; un obstaculo siempre detiene."""
    if orden is not None:
        estado = orden
    if distancia is None or distancia <= DISTANCIA_MINIMA:
        estado = "detener"
    return estado


def hay_cambio(anterior, actual):
    """Comparar con el ultimo dato impreso, no con la ultima medicion."""
    if anterior is None:
        return True
    distancia, estado, potencia = actual
    distancia_previa, estado_previo, potencia_previa = anterior
    if estado != estado_previo or potencia != potencia_previa:
        return True
    if distancia is None or distancia_previa is None:
        return distancia != distancia_previa
    return abs(distancia - distancia_previa) >= CAMBIO_DISTANCIA_CM


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
    ultimo_reporte = None
    datos_reportados = None
    print("PARCIAL 2 - Vehiculo con pulsadores")
    print("Una pulsacion selecciona movimiento; el rojo detiene.")
    print("Potenciometro: potencia de 0 a 100 %. Obstaculo: 20 cm.")
    print("El monitor muestra solo cambios; el control sigue funcionando.")

    try:
        while True:
            activos = [nombre for nombre, pin in botones.items() if pin.value() == 0]
            if "detener" in activos or len(activos) > 1:
                pulsado = "detener"
            else:
                pulsado = activos[0] if activos else None
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

            # Solo cambia la salida de texto: el sensor y los botones siguen
            # atendiendose en cada ciclo como en la version original.
            ahora = ticks_ms()
            potencia = velocidad if estado != "detener" else 0
            datos = (distancia, estado, potencia)
            cambio_estado = datos_reportados is None or estado != datos_reportados[1]
            puede_reportar = (ultimo_reporte is None or cambio_estado or
                              ticks_diff(ahora, ultimo_reporte) >= 500)
            if puede_reportar and hay_cambio(datos_reportados, datos):
                lectura = "sin lectura" if distancia is None else "%.1f cm" % distancia
                print("Distancia: %s | Estado: %s | PWM: %d %%" % (lectura, estado, potencia))
                datos_reportados = datos
                ultimo_reporte = ahora
            sleep_ms(20)
    finally:
        motores.detener()


if __name__ == "__main__":
    main()
