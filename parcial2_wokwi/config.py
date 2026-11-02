"""Configuracion para Wokwi. Usar el mismo TOPIC_BASE en el cliente MQTT."""
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
WIFI_TIMEOUT_MS = 12000

# Broker publico de pruebas: no enviar datos privados. Solo simulacion.
MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_KEEPALIVE_S = 10
CONNECT_TIMEOUT_S = 2
# Cambiar el sufijo si otra persona copia el proyecto y lo ejecuta a la vez.
TOPIC_BASE = "parcial2/vehiculo_7d49c2a1"

ESTOP_PIN = 13                 # Pulsador normalmente abierto entre GPIO13 y GND.
MAX_SPEED = 100                # Porcentaje de PWM, no velocidad medida.
OBSTACLE_CM = 20
SENSOR_PERIOD_MS = 100
SENSOR_STALE_MS = 350
MOVE_TIMEOUT_MS = 800          # La app repite move cada 250 ms al mantener pulsado.
CONTROL_TIMEOUT_MS = 1500      # heartbeat mantiene arm activo cuando esta detenido.
TELEMETRY_MS = 500
HEARTBEAT_MS = 1000
LOOP_MS = 10
