# Parcial 2 — Vehículo simulado en Wokwi

Firmware en **MicroPython sobre ESP32** que lee distancia y controla las señales de dos motores. Se ejecuta completamente en Wokwi.

## Archivos

| Archivo | Función |
|---|---|
| `main.py` | Lee los controles, decide el movimiento y muestra el estado |
| `motores.py` | Genera dirección y PWM para los dos motores |
| `sensor.py` | Lee la distancia del HC-SR04 |
| `diagram.json` | Componentes y conexiones de Wokwi |
| `README.md` | Descripción e instrucciones |

## Componentes simulados

Una ESP32, un HC-SR04, cinco botones, un potenciómetro y seis LED con resistencias de 220 Ω. Los LED representan las **señales de control** de los motores; no simulan un carro desplazándose ni un L298N físico.

## Ejecutar

1. Abrir [Nuevo proyecto ESP32 con MicroPython](https://wokwi.com/projects/new/micropython-esp32).
2. Reemplazar `main.py` y `diagram.json` por los archivos de esta carpeta.
3. Añadir `motores.py` y `sensor.py` desde el menú del editor. Copiar sus contenidos; los cuatro archivos deben estar en la raíz del proyecto Wokwi.
4. Pulsar **Start the simulation**.
5. Pulsar un botón de dirección. La orden permanece activa hasta otra pulsación o una parada automática. El botón rojo detiene.
6. Girar el potenciómetro para cambiar el PWM. Si llega a cero, se detiene y requiere una nueva pulsación para volver a mover.
7. Hacer clic en el HC-SR04 y cambiar la distancia. A **20 cm o menos**, o si la lectura falla, el programa detiene todas las salidas.
8. Observar distancia, estado y PWM en el monitor serie.

Después de una parada por obstáculo, aumentar la distancia y volver a pulsar una dirección. Despejar el sensor no reinicia por sí solo. Presionar varios botones a la vez también detiene.

## Conexiones de la simulación

| Elemento | GPIO |
|---|---|
| HC-SR04 TRIG / ECHO | 23 / 34 |
| Avanzar / retroceder | 32 / 33 |
| Izquierda / derecha / detener | 21 / 22 / 13 |
| Potenciómetro SIG | 35 |
| LED ENA / ENB (PWM) | 25 / 14 |
| LED IN1 / IN2 / IN3 / IN4 | 26 / 27 / 18 / 19 |

Los botones se conectan a GND y usan `PULL_UP`. Cada LED tiene resistencia de 220 Ω. El potenciómetro usa 3V3 y GND; el sensor, VIN y GND. El ECHO directo corresponde **exclusivamente a esta simulación digital**; no copiar ese cableado a hardware físico.

## Pruebas para mostrar al docente

| Prueba | Resultado esperado |
|---|---|
| Iniciar | Salidas detenidas |
| Distancia 100 cm y avanzar | IN1 e IN3 activos; ENA/ENB con PWM |
| Retroceder | IN2 e IN4 activos |
| Izquierda | IN2 e IN3 activos |
| Derecha | IN1 e IN4 activos |
| Cambiar potenciómetro | Varía PWM indicado y brillo de ENA/ENB |
| Detener | Todos los LED apagados |
| Distancia de 10 cm durante movimiento | Parada automática |
| Volver a 100 cm sin otra pulsación | Permanece detenido |

## Entrega del Parcial 2

Se incluyen firmware MicroPython, sensor, entradas digitales y analógica, salidas digitales y PWM, procesamiento de distancia, módulos y README. Completar la entrega con el repositorio GitHub y el enlace de la simulación guardada.

**Enlace Wokwi:** pendiente de guardar en una cuenta.

Guardar cambios reales de cada etapa en Git: sensor, motores, controles y pruebas. Para un repositorio nuevo que contenga solamente esta versión, copiar **estos cinco archivos** a otra carpeta y ejecutar allí:

```powershell
git init -b main
git add .
git commit -m "feat: agregar simulacion del vehiculo para el parcial 2"
git remote add origin https://github.com/TU_USUARIO/vehiculo-parcial2.git
git push -u origin main
```

Crear antes un repositorio vacío en GitHub y sustituir la URL. Continuar con commits de las pruebas y correcciones efectivamente realizadas. No hacen falta PyCharm ni componentes físicos para ejecutar la simulación.

**Validación:** sintaxis y lógica de movimiento/parada comprobadas en el computador con periféricos simulados por software. No se ejecutó el proyecto en Wokwi: la carga de archivos al sitio no fue autorizada en esta sesión. Las pruebas de la tabla son pasos por realizar, no resultados ya obtenidos.

Referencia: [simulación ESP32 en Wokwi](https://docs.wokwi.com/guides/esp32).
