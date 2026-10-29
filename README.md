# Vehículo móvil con ESP32, MicroPython y MQTT — Parcial 2

Proyecto de Programación II: carro de dos motores que recibe órdenes por MQTT y publica distancia, movimiento y estado de seguridad. El Parcial 2 se concentra en el **firmware**; el contrato de comunicación permite incorporar una aplicación de escritorio en el Parcial 3.

**Placa de referencia:** ESP32 DevKit clásica / ESP32-WROOM-32, 4 MB de flash. El pinout no es intercambiable con ESP32-C3/S3. **Estado inicial:** motores deshabilitados; es necesario configurar la red y armar explícitamente el vehículo.

## Lectura y ejecución por etapas

1. [Alcance, objetivos y arquitectura](docs/01_arquitectura.md).
2. [Materiales, pinout y montaje eléctrico](docs/02_montaje.md). Leer antes de conectar energía.
3. [Entorno Windows, PyCharm, carga y GitHub](docs/03_entorno.md).
4. [Contrato MQTT y seguridad](docs/04_mqtt.md).
5. [Pruebas y criterios de aceptación](docs/05_pruebas.md).
6. [Correspondencia con los requisitos del Parcial 2](docs/06_rubrica.md).
7. [Base de la aplicación del Parcial 3](docs/07_parcial3.md).
8. [Fuentes técnicas](docs/FUENTES.md) y [registro de validación](evidence/VALIDACION.md).

## Componentes

ESP32, módulo L298N con disipador y diodos, dos motores DC y chasis, HC-SR04, fuente de motores adecuada, fuente regulada de 5 V para lógica, resistencias para divisor de ECHO y estados seguros, interruptor de emergencia de dos contactos normalmente cerrados, fusible y cableado. La selección de fuente, fusible y corriente se completa a partir de los motores reales; no se presupone que cualquier módulo L298N soporte 2 A continuos.

## Estructura

```text
firmware/       MicroPython: control, sensores, motores, Wi-Fi y transporte MQTT
tools/          cliente de consola, carga a placa y empaquetado Wokwi
tests/          pruebas de seguridad y protocolo ejecutables en el computador
broker/         configuración de Mosquitto para laboratorio
simulation/     diagram.json, configuración de ejemplo y guía Wokwi
docs/           explicación académica, montaje, instalación y Parcial 3
diagrams/       esquemas SVG y fuente Mermaid editables
evidence/       resultados verificables y plantilla de pruebas físicas
.run/           configuración compartida de pruebas para PyCharm
```

## Comprobaciones en el computador

Desde la raíz, con Python 3.12 o superior:

```powershell
python -m unittest discover -s tests -v
python tools/check_project.py
```

Estas pruebas no requieren motores, broker ni dependencias externas. Compilar sintaxis con CPython no demuestra compatibilidad completa con MicroPython ni funcionamiento físico. Los resultados reales están en `evidence/VALIDACION.md`.

## Puesta en marcha resumida

1. Instalar las herramientas PC de `requirements-dev.txt` en `.venv`.
2. Preparar el broker según `broker/README.md`.
3. Copiar `firmware/config_local.example.py` como `firmware/config_local.py`; definir Wi-Fi, IP del broker, usuario, contraseña y un identificador único.
4. Instalar MicroPython para la placa correcta y cargar con `tools/upload.ps1`.
5. Con ruedas levantadas, verificar ECHO, parada física, estados y timeout antes de permitir desplazamientos.
6. Ejecutar `tools/console.py` para observar telemetría y hacer movimientos de duración limitada.

No ejecutar `firmware/main.py` con Python de Windows: utiliza los periféricos de MicroPython. La batería no se mide en esta entrega; `battery_v` se publica como `null`.

## Simulación y repositorio

Los archivos Wokwi se preparan mediante `python tools/build_wokwi.py`. Véase [simulation/README.md](simulation/README.md). El montaje simulado representa las órdenes a los motores con LED y analizador lógico; no reproduce un L298N ni la dinámica del carro. **Enlace de la simulación: pendiente de crear y guardar en Wokwi.** No se presenta un enlace ficticio como evidencia.

El historial local registra etapas reales de preparación de esta entrega, todas en la fecha de trabajo. No sustituye el desarrollo y las pruebas del estudiante a lo largo del curso. La publicación en GitHub requiere crear el repositorio en la cuenta elegida; las instrucciones están en la guía del entorno.
