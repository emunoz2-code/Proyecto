# Validación de la adaptación MQTT del Parcial 2

Fecha: 2 de noviembre de 2026. Alcance: carpeta `parcial2_wokwi`.

## Resultado local

Comando desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s verificacion_wokwi -v
```

Resultado actualizado: 46 pruebas aprobadas en CPython. Se usan periféricos y sockets dobles, sin una ESP32 ni un broker real.

- `test_control.py`: 21 casos de comandos, sesiones, secuencias, emergencia, sensor, desconexión lógica y límites de tiempo.
- `test_hardware_adapters.py`: 6 casos de señales de motor/PWM y conversión/fallos del sensor.
- `test_mqtt.py`: 15 casos de tramas MQTT, conexión simulada, mensajes retenidos, fragmentación TCP y límites de colas/plazos.
- `test_ejemplo_clase.py`: 4 casos del adaptador ClienteMQTT (suscripción, comando retenido, movimiento y publicación) y conexión Wi-Fi disponible, existente o con plazo agotado.
- Sintaxis: nueve módulos `.py` aceptados por el analizador de Python; no certifica todas las API del firmware MicroPython instalado en Wokwi.
- Diagrama: 15 componentes funcionales y dos textos, IDs únicos y conexiones referidas a partes existentes. Un solo botón, sin potenciómetro.

## Prueba externa incompleta

Se intentó conectar un cliente Paho independiente a `test.mosquitto.org:1883` para intercambiar mensajes de prueba con el cliente del firmware ejecutado en CPython. Se utilizó un topic temporal aleatorio separado del vehículo. La conexión TCP del primer cliente agotó su plazo de 3 s antes de realizar el intercambio. No se verificó MQTT con un broker real. No se atribuye la causa a la red o al broker sin evidencia adicional.

## Pendiente

- Cargar y ejecutar los módulos en Wokwi, comprobar el enlace MQTT y observar las salidas.
- Realizar las pruebas de demostración indicadas en el README.
- Guardar el enlace del proyecto Wokwi.

La sesión conserva un bloqueo de acceso del navegador a Wokwi; no se intentó eludirlo. No se realizaron pruebas físicas ni se implementó la interfaz del Parcial 3.
