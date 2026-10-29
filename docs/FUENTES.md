# Fuentes técnicas consultadas

Consulta: 29 de octubre de 2026. Se priorizaron documentación de fabricantes, especificación del protocolo y manuales oficiales. Las páginas `latest` pueden describir una versión de desarrollo; registrar la versión estable instalada y verificar sus API antes del ensayo físico.

| Fuente | Uso en el proyecto |
|---|---|
| [Espressif: hoja de datos ESP32](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) | Niveles eléctricos y límites de entradas |
| [Espressif: GPIO ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) | Pines de arranque, memoria y entradas GPIO34–39 |
| [ST: hoja de datos L298](https://www.st.com/resource/en/datasheet/l298.pdf) | Alimentación lógica, niveles TTL, caída y disipación |
| [MicroPython: ESP32 quick reference](https://docs.micropython.org/en/latest/esp32/quickref.html) | GPIO, PWM, WLAN y WDT |
| [MicroPython: funciones machine](https://docs.micropython.org/en/latest/library/machine.html) | time_pulse_us y códigos de timeout |
| [MicroPython: socket](https://docs.micropython.org/en/latest/library/socket.html) | Operaciones no bloqueantes y limitaciones |
| [MicroPython: ESP32_GENERIC](https://micropython.org/download/ESP32_GENERIC/) | Elección e instalación del firmware |
| [MicroPython: mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) | Transferencia de archivos y consola serie |
| [OASIS: MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html) | Formato de paquetes, voluntad, sesiones y retención |
| [Eclipse Paho Python](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html) | Cliente de consola y callbacks versión 2 |
| [Mosquitto: configuración](https://mosquitto.org/man/mosquitto-conf-5.html) | Listener, autenticación y ACL |
| [Mosquitto: descarga](https://mosquitto.org/download/) | Instalación del broker local |
| [Mosquitto: servicio de pruebas](https://test.mosquitto.org/) | Puerto público para simulación únicamente |
| [Wokwi: ESP32](https://docs.wokwi.com/guides/esp32) | Alcance de simulación de ESP32 |
| [Wokwi: formato de diagrama](https://docs.wokwi.com/diagram-format) | Archivo editable diagram.json |
| [Wokwi: HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04) | Modelo simulado, pulso TRIG y conversión tiempo/distancia |
| [Wokwi: Wi-Fi](https://docs.wokwi.com/guides/esp32-wifi) | Wokwi-GUEST y gateway |
| [Wokwi: MicroPython](https://docs.wokwi.com/guides/micropython) | Archivos de programa y ejecución |
| [Git: instalación Windows](https://git-scm.com/install/windows) | Instalación y verificación |
| [JetBrains: instalación PyCharm](https://www.jetbrains.com/help/pycharm/installation-guide.html) | Entorno de edición |
| [JetBrains: intérpretes virtuales](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html) | Entorno local del proyecto |
| [GitHub: subir código local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) | Publicación y remoto |

El HC-SR04 y los módulos L298N tienen variantes comerciales: la documentación de simulación o del integrado no reemplaza la ficha del módulo adquirido. El cálculo del divisor, selección conservadora de pines y decisiones de parada son parte del diseño de esta entrega.
