"""Valores comunes. Copiar el ejemplo local para configurar una placa real."""
DEVICE_ID = "carro01"
TOPIC_ROOT = "prog2/equipo01"
WIFI_SSID = "CONFIGURAR"
WIFI_PASSWORD = ""
MQTT_HOST = "192.168.1.10"
MQTT_PORT = 1883
MQTT_USER = "carro"
MQTT_PASSWORD = "CONFIGURAR"
MQTT_KEEPALIVE_S = 10
CONNECT_TIMEOUT_S = 2
WIFI_TIMEOUT_MS = 12000
WDT_MS = 5000

ENA, IN1, IN2 = 25, 26, 27
ENB, IN3, IN4 = 14, 18, 19
TRIG, ECHO = 23, 34
ESTOP_PIN = 33  # NC a GND: abierto/alto significa emergencia.
PWM_HZ = 1000
INVERT_LEFT = False
INVERT_RIGHT = False
MAX_SPEED = 60
OBSTACLE_CM = 20
SENSOR_PERIOD_MS = 100
SENSOR_STALE_MS = 350
ECHO_TIMEOUT_US = 25000
MOVE_TIMEOUT_MS = 600
CONTROL_TIMEOUT_MS = 1000
TELEMETRY_MS = 500
HEARTBEAT_MS = 1000
LOOP_MS = 10

try:
    from config_local import *
except ImportError as exc:
    # No ocultar importaciones rotas dentro de un archivo local existente.
    if "config_local" not in str(exc):
        raise
