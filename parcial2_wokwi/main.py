"""Parcial 2: ESP32 en Wokwi preparada para control desde una app por MQTT."""
import json
import os
import binascii
from time import sleep_ms
from machine import Pin
import config as cfg
from clockutil import now_ms, elapsed
from motores import Motores
from sensor import SensorDistancia
from control import Controller
from cliente_mqtt import ClienteMQTT
from red import conectar


def token():
    """Identificador nuevo para descartar ordenes de una sesion anterior."""
    return binascii.hexlify(os.urandom(8)).decode()


def main():
    motores = Motores()
    mqtt = None
    try:
        if not cfg.TOPIC_BASE or any(c in cfg.TOPIC_BASE for c in "+#\x00"):
            raise ValueError("TOPIC_BASE invalido")
        if not 1 <= cfg.MAX_SPEED <= 100:
            raise ValueError("MAX_SPEED debe estar entre 1 y 100")
        sensor = SensorDistancia(trig=23, echo=34)
        boton_rojo = Pin(cfg.ESTOP_PIN, Pin.IN, Pin.PULL_UP)
        control = Controller(motores, cfg, token)
        base = cfg.TOPIC_BASE.rstrip("/")
        client_id = "esp32-" + token()

        def servicio_detenido():
            # Las conexiones pueden esperar; se realizan sin movimiento.
            motores.detener()
            control.physical(boton_rojo.value() == 0)

        def recibir(topic, payload, retained):
            control.physical(boton_rojo.value() == 0)
            if topic.decode() == base + "/cmd":
                respuesta = control.command(payload, retained, now_ms())
                mqtt.publicar(base + "/ack", json.dumps(respuesta))
                mqtt.publicar(base + "/telemetry", json.dumps(control.snapshot(now_ms())))

        mqtt = ClienteMQTT(client_id, cfg.MQTT_HOST, base)
        mqtt.suscribir(base + "/cmd", recibir)
        espera = 1000
        print("PARCIAL 2 - Control remoto MQTT")
        print("Broker:", cfg.MQTT_HOST, "| Topics:", base + "/#")
        print("Sin orden remota valida, el vehiculo permanece detenido.")
        while True:
            control.link(False)
            try:
                servicio_detenido()
                wifi = conectar(cfg.WIFI_SSID, cfg.WIFI_PASSWORD,
                                servicio_detenido, cfg.WIFI_TIMEOUT_MS)
                mqtt.conectar()
                while not mqtt.listo:
                    servicio_detenido()
                    mqtt.recibirmensaje()
                    sleep_ms(cfg.LOOP_MS)
                control.link(True)
                mqtt.publicar(base + "/availability", '{"v":1,"online":true}', True)
                print("Conectado. Esperando arm y move desde el cliente MQTT.")
                ultimo_sensor = ultima_telemetria = ultimo_latido = None
                numero_latido = 0
                conectado_desde = now_ms()
                while wifi.isconnected():
                    ahora = now_ms()
                    control.physical(boton_rojo.value() == 0)
                    # Caducar antes de renovar sensor o procesar mensajes tardios.
                    control.tick(ahora)
                    if ultimo_sensor is None or elapsed(ahora, ultimo_sensor) >= cfg.SENSOR_PERIOD_MS:
                        distancia = sensor.leer_cm()
                        ultimo_sensor = now_ms()
                        control.sensor(distancia, ultimo_sensor)
                    control.physical(boton_rojo.value() == 0)
                    control.tick(now_ms())
                    mqtt.recibirmensaje()  # No bloquea al recibir tramas incompletas.
                    ahora = now_ms()
                    control.tick(ahora)
                    if ultima_telemetria is None or elapsed(ahora, ultima_telemetria) >= cfg.TELEMETRY_MS:
                        estado = control.snapshot(ahora)
                        mqtt.publicar(base + "/telemetry", json.dumps(estado))
                        print(json.dumps(estado))
                        ultima_telemetria = ahora
                    if ultimo_latido is None or elapsed(ahora, ultimo_latido) >= cfg.HEARTBEAT_MS:
                        mqtt.publicar(base + "/heartbeat", json.dumps({
                            "v": 1, "seq": numero_latido, "uptime_ms": ahora}))
                        numero_latido += 1
                        ultimo_latido = ahora
                    if elapsed(ahora, conectado_desde) > 10000:
                        espera = 1000
                    sleep_ms(cfg.LOOP_MS)
                raise OSError("Wi-Fi desconectado")
            except (OSError, ValueError) as exc:
                control.link(False)
                mqtt.cerrar()
                print("Sin conexion:", exc, "| Reintento en ms:", espera)
                inicio = now_ms()
                while elapsed(now_ms(), inicio) < espera:
                    servicio_detenido()
                    sleep_ms(50)
                espera = min(espera * 2, 10000)
    finally:
        motores.detener()
        if mqtt:
            mqtt.cerrar()


if __name__ == "__main__":
    main()
