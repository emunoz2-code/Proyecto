import network
from time import sleep

def conectar(ssid, password):
    wifi = network.WLAN( network.STA_IF)
    wifi.active(True)

    wifi.connect(ssid, password)

    print("Conectando...")
    while not wifi.isconnected():
        sleep(0.5)
    print("Conectado")
    print(wifi.ifconfig())
