# Parcial 2: vehículo con pulsadores en Wokwi

Firmware desarrollado en **MicroPython para una ESP32**, con lectura de distancia, cinco pulsadores, control de potencia con potenciómetro y señales digitales/PWM representadas mediante LED.

**Simulación del estudiante:** [abrir proyecto en Wokwi](https://wokwi.com/projects/479614304886635521).

Esta carpeta reúne la versión con pulsadores explicada en la sustentación. No requiere Wi-Fi, broker MQTT ni aplicación de escritorio.

## Archivos necesarios

| Archivo | Qué hace |
|---|---|
| `main.py` | Configura entradas, procesa las órdenes, aplica las paradas y muestra cambios en el monitor serie. |
| `motores.py` | Contiene la clase `Motores`, que genera las cuatro señales de dirección y las dos señales PWM. |
| `sensor.py` | Contiene la clase `SensorDistancia`, que mide el pulso ECHO y calcula centímetros. |
| `diagram.json` | Describe los componentes y conexiones del montaje local reproducible. |
| `LEEME.md` | Explica la corrección que evita repetir constantemente los mismos datos. |

Los tres archivos Python y `diagram.json` deben quedar juntos en la raíz del proyecto Wokwi. No ejecutar `main.py` con Python de Windows: necesita los periféricos de MicroPython.

## Componentes y conexiones

| Cantidad | Elemento | Conexión o función |
|---:|---|---|
| 1 | ESP32 DevKit V1 | Ejecuta el firmware. |
| 1 | HC-SR04 | TRIG a GPIO 23; ECHO a GPIO 34; VCC a VIN; GND a GND. |
| 5 | Pulsadores | Avanzar: GPIO 32; retroceder: 33; izquierda: 21; derecha: 22; detener: 13. Cada botón conecta su GPIO a GND al pulsarlo. |
| 1 | Potenciómetro | SIG a GPIO 35; VCC a 3V3; GND a GND. |
| 4 | LED de dirección | IN1: GPIO 26; IN2: 27; IN3: 18; IN4: 19. |
| 2 | LED de PWM | ENA: GPIO 25; ENB: GPIO 14. |
| 6 | Resistencias de 220 Ω | Una en serie con cada LED: GPIO → resistencia → ánodo; cátodo → GND. |

Los pulsadores utilizan `Pin.PULL_UP`: sin pulsar se lee 1 y al pulsar se lee 0. El potenciómetro se lee con un ADC de 12 bits, de 0 a 4095, y el código lo convierte a un porcentaje de 0 a 100.

Los seis LED permiten observar las **señales destinadas a dos motores**. No hay motores DC ni un L298N simulados en esta entrega; no se demuestra desplazamiento ni velocidad física. El porcentaje indica PWM aplicado, no una velocidad medida. El ECHO conectado directamente corresponde solo a la simulación digital y no es un esquema para montar hardware físico.

## Funcionamiento

1. Al iniciar, todas las salidas quedan detenidas. Se configura el sensor, los botones y el potenciómetro.
2. El programa revisa los botones en un bucle con una pausa de 20 ms. Una pulsación selecciona un movimiento que se conserva al soltar el botón.
3. La distancia se vuelve a medir aproximadamente cada 100 ms. Si es de 20 cm o menos, o la lectura no es válida, se detiene cualquier movimiento, incluido retroceder.
4. El potenciómetro determina el PWM de ambos canales. Al llegar a cero, el estado cambia a detener.
5. El botón rojo o varios botones pulsados simultáneamente ordenan detener. Tras una parada automática se necesita una nueva pulsación de dirección; despejar el sensor o subir el potenciómetro no reinicia por sí solo.
6. El monitor muestra distancia, estado y PWM cuando cambian. Los cambios de estado se informan en el ciclo que los detecta; los otros reportes tienen una separación mínima de 500 ms y los cambios de distancia inferiores a 1 cm no generan un reporte por sí solos.
7. `finally` llama a `motores.detener()` al salir del bucle por una excepción o interrupción que llegue al intérprete. No equivale a una parada física de emergencia.

| Orden | IN1 | IN2 | IN3 | IN4 |
|---|---:|---:|---:|---:|
| Avanzar | 1 | 0 | 1 | 0 |
| Retroceder | 0 | 1 | 0 | 1 |
| Izquierda | 0 | 1 | 1 | 0 |
| Derecha | 1 | 0 | 0 | 1 |
| Detener | 0 | 0 | 0 | 0 |

ENA y ENB usan PWM de 1000 Hz, con `duty` de 0 a 1023. Al detener, ambos quedan en cero.

## Ejecutar y comprobar en Wokwi

Abrir el enlace de la simulación y pulsar iniciar. Para reproducir los archivos locales, crear un proyecto **ESP32 con MicroPython** y copiar `main.py`, `motores.py`, `sensor.py` y `diagram.json` de esta carpeta. El diagrama local recupera las conexiones del montaje original; su distribución visual puede diferir de la versión acomodada por el estudiante en Wokwi.

| Acción | Resultado esperado |
|---|---|
| Iniciar sin pulsar controles | Estado detener y PWM 0 %. |
| Poner distancia en 100 cm, subir el potenciómetro y pulsar avanzar | IN1 e IN3 activos y PWM en ENA/ENB. |
| Pulsar las otras direcciones | Cambian los LED según la tabla anterior. |
| Girar el potenciómetro durante la marcha | Cambia el porcentaje de PWM. |
| Pulsar el botón rojo | Todas las señales quedan en cero. |
| Durante la marcha, seleccionar el HC-SR04 y poner 10 cm | Parada automática. |
| Volver a 100 cm sin pulsar una dirección | Continúa detenido. |
| Volver a pulsar una dirección con potencia mayor que cero | Reanuda el movimiento solicitado. |
| Mantener sin cambios sensor, estado y potencia | No se repite constantemente la misma línea en el monitor. |

Estas son pruebas propuestas para ejecutar y mostrar al docente, no una lista de pruebas ya realizadas en Wokwi por el asistente.

## Alcance de la validación

La revisión local de esta preparación comprueba sintaxis y coherencia entre conexiones y GPIO. No sustituye ejecutar el firmware en MicroPython. El estudiante aportó anteriormente una captura del montaje funcionando y suministró el enlace de Wokwi; no se verificó que el contenido actual de ese enlace coincida exactamente con esta carpeta. No se realizaron pruebas físicas.

## Correspondencia con el Parcial 2

Se incluyen firmware MicroPython, lectura del sensor, entradas digitales y analógica, salidas digitales y PWM, decisiones de control, funciones, clases y módulos. La organización y el enlace de simulación quedan documentados; los commits se conservan en el historial Git del repositorio. La representación de actuadores mediante LED debe explicarse durante la sustentación.
