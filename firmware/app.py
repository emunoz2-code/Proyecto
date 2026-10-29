"""Orquestación del vehículo; ningún fallo de red conserva la marcha."""
import json
import os
import binascii
from time import sleep_ms
from machine import Pin, WDT, unique_id
import config as cfg
from clockutil import now_ms, elapsed
from motor import Motors
from ultrasonic import Ultrasonic
from control import Controller
from mqtt_wire import MQTTClient
from wifi import WiFi


def token():
    return binascii.hexlify(os.urandom(8)).decode()


def run():
    motors = Motors(cfg)
    mqtt = None
    control = None
    try:
        if not 1 <= cfg.MAX_SPEED <= 100:
            raise ValueError("MAX_SPEED debe estar entre 1 y 100")
        if not cfg.TOPIC_ROOT or any(c in cfg.TOPIC_ROOT for c in "+#\x00"):
            raise ValueError("TOPIC_ROOT inválido")
        if not cfg.DEVICE_ID or any(c in cfg.DEVICE_ID for c in "/+#\x00"):
            raise ValueError("DEVICE_ID inválido")
        sensor = Ultrasonic(cfg)
        emergency = Pin(cfg.ESTOP_PIN, Pin.IN, Pin.PULL_UP)
        control = Controller(motors, cfg, token)
        watchdog = WDT(timeout=cfg.WDT_MS)
        wifi = WiFi(cfg)
        base = cfg.TOPIC_ROOT.rstrip("/") + "/" + cfg.DEVICE_ID
        client_id = cfg.DEVICE_ID + "-" + binascii.hexlify(unique_id()).decode()

        def safe_service():
            motors.stop()
            control.physical(emergency.value())
            watchdog.feed()

        def on_message(topic, payload, retained):
            control.physical(emergency.value())
            if topic == base + "/cmd":
                result = control.command(payload, retained, now_ms())
                mqtt.publish(base + "/ack", json.dumps(result))

        mqtt = MQTTClient(cfg, on_message)
        delay = 500
        while True:
            # Toda conexión/reconexión comienza desarmada.
            control.link(False)
            try:
                safe_service()
                wifi.connect(safe_service)
                mqtt.connect(client_id, base)
                start = now_ms()
                while not mqtt.ready:
                    safe_service()
                    mqtt.poll()
                    if elapsed(now_ms(), start) >= 3500:
                        raise OSError("Suscripción no confirmada")
                    sleep_ms(10)
                control.link(True)
                mqtt.publish(base + "/availability", '{"v":1,"online":true}', True)
                print("MQTT conectado:", base)
                last_sensor = last_telemetry = last_heartbeat = None
                heart_seq = 0
                stable_at = now_ms()
                while wifi.connected():
                    now = now_ms()
                    control.physical(emergency.value())
                    # Comprobar vencimientos ANTES de renovar lecturas o recibir órdenes.
                    control.tick(now)
                    if last_sensor is None or elapsed(now, last_sensor) >= cfg.SENSOR_PERIOD_MS:
                        value = sensor.read_cm()
                        last_sensor = now_ms()
                        control.sensor(value, last_sensor)
                    now = now_ms()
                    control.physical(emergency.value())
                    control.tick(now)
                    mqtt.poll()
                    control.tick(now_ms())
                    if last_telemetry is None or elapsed(now, last_telemetry) >= cfg.TELEMETRY_MS:
                        mqtt.publish(base + "/telemetry", json.dumps(control.snapshot(now)))
                        last_telemetry = now
                    if last_heartbeat is None or elapsed(now, last_heartbeat) >= cfg.HEARTBEAT_MS:
                        mqtt.publish(base + "/heartbeat", json.dumps({"v": 1, "seq": heart_seq, "uptime_ms": now}))
                        heart_seq += 1
                        last_heartbeat = now
                    if elapsed(now, stable_at) > 10000:
                        delay = 500
                    watchdog.feed()
                    sleep_ms(cfg.LOOP_MS)
                raise OSError("Wi-Fi desconectado")
            except (OSError, ValueError) as exc:
                control.link(False)
                mqtt.close()
                print("Conexión interrumpida:", exc, "Reintento ms:", delay)
                start = now_ms()
                while elapsed(now_ms(), start) < delay:
                    safe_service()
                    sleep_ms(50)
                delay = min(delay * 2, 10000)
    finally:
        motors.stop()
        if control:
            control.disarm("shutdown")
        if mqtt:
            mqtt.close()
        # El WDT puede reiniciar tras Ctrl+C; la placa vuelve desarmada.
