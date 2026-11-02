"""Conexion Wi-Fi basada en el ejemplo de clase, con plazo y parada local."""
import network
from time import sleep_ms
from clockutil import now_ms, elapsed


def conectar(ssid, password, servicio_seguro=None, timeout_ms=12000):
    """Devuelve WLAN para consultar isconnected() durante el programa.

    Llamar solo con motores detenidos. servicio_seguro mantiene las salidas
    apagadas y atiende el boton rojo mientras se espera la conexion.
    """
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if servicio_seguro:
        servicio_seguro()
    if not wifi.isconnected():
        try:
            wifi.disconnect()
        except OSError:
            pass
        print("Conectando a Wi-Fi...")
        inicio = now_ms()
        wifi.connect(ssid, password)
        while not wifi.isconnected():
            if servicio_seguro:
                servicio_seguro()
            if elapsed(now_ms(), inicio) >= timeout_ms:
                raise OSError("Tiempo de conexion Wi-Fi agotado")
            sleep_ms(50)
    print("Conectado a Wi-Fi:", wifi.ifconfig())
    return wifi
