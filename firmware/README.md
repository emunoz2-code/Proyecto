# Vehículo con ESP32 - Parcial 2

Proyecto en MicroPython para controlar las señales de un carro desde cinco pulsadores. Se usa un sensor ultrasónico para detectar obstáculos y un potenciómetro para cambiar la potencia.

[Ver simulación en Wokwi](https://wokwi.com/projects/479614304886635521)

## Componentes

- 1 ESP32.
- 1 sensor HC-SR04.
- 5 pulsadores: avanzar, retroceder, izquierda, derecha y detener.
- 1 potenciómetro.
- 6 LED y 6 resistencias de 220 ohmios.

Los LED representan las señales de dirección y PWM de dos motores. En este montaje no hay motores reales ni se simula el desplazamiento del carro.

## Archivos

- `main.py`: lee los botones y el potenciómetro, consulta la distancia y decide el movimiento.
- `motores.py`: genera las señales de dirección y PWM.
- `sensor.py`: obtiene la distancia del HC-SR04.
- `diagram.json`: guarda los componentes y conexiones de Wokwi.

## Conexiones

| Elemento | GPIO |
|---|---|
| Sensor TRIG / ECHO | 23 / 34 |
| Avanzar / retroceder | 32 / 33 |
| Izquierda / derecha / detener | 21 / 22 / 13 |
| Potenciometro SIG | 35 |
| Direccion IN1 / IN2 / IN3 / IN4 | 26 / 27 / 18 / 19 |
| PWM ENA / ENB | 25 / 14 |

Los botones conectan su GPIO a GND y usan la resistencia interna PULL_UP. El potenciómetro se conecta a 3V3 y GND. Cada LED lleva una resistencia en serie y su cátodo va a GND. El sensor usa VIN y GND. La conexión directa de ECHO corresponde solo a esta simulación, no a un montaje físico.

## Funcionamiento

El programa inicia detenido. Al pulsar una dirección, mantiene esa orden hasta recibir otra o detectar una condición de parada. El potenciómetro ajusta el PWM entre 0 y 100 %; ese porcentaje no es una velocidad medida.

El carro se detiene si se pulsa el boton rojo, se presionan varios botones al tiempo, la potencia llega a cero, la distancia es de 20 cm o menos o el sensor no entrega una lectura válida. Después de una parada automática se debe volver a pulsar una dirección para continuar.

El monitor serie muestra distancia, estado y PWM cuando cambian. Si todo permanece igual, no repite constantemente los mensajes.

## Cómo ejecutarlo

Abrir el enlace de Wokwi e iniciar la simulación. Para reproducir esta copia, crear un proyecto ESP32 con MicroPython y copiar juntos `main.py`, `motores.py`, `sensor.py` y `diagram.json` en el editor. El diagrama local puede tener una distribución visual diferente a la del enlace.

Con el sensor en 100 cm, subir el potenciómetro y probar los botones de dirección. Luego cambiar la distancia a 10 cm para comprobar la parada. Al volver a 100 cm debe permanecer detenido hasta una nueva pulsación. Comprobar también el boton rojo y la potencia en cero.

## Revisión

Se revisaron la sintaxis de los archivos Python y las conexiones del diagrama en el computador. Esto no reemplaza la prueba en Wokwi. No se hicieron pruebas con componentes físicos ni se comprobó que la versión actual del enlace coincida exactamente con estos archivos.
