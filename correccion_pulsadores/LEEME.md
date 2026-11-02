# Corrección del monitor serie del montaje con pulsadores

Aplicar a la versión original que tiene cinco pulsadores, un potenciómetro, HC-SR04, seis LED y ESP32. Es la versión mostrada en la captura del usuario, anterior a la adaptación MQTT.

## Aplicar

1. Detener la simulación de Wokwi.
2. Abrir el `main.py` de ese proyecto y reemplazar todo su contenido por el `main.py` de esta carpeta.
3. Conservar sus archivos `motores.py`, `sensor.py` y `diagram.json`; no modificar los cables.
4. Iniciar nuevamente la simulación.

Este archivo no se debe usar como reemplazo del programa principal MQTT. No necesita los módulos de comunicación.

## Qué cambia

El programa anterior imprimía distancia, estado y PWM cada 500 ms aunque todo siguiera igual. Eso era un reporte periódico, no un error ni una nueva orden de movimiento.

La corrección imprime una vez al iniciar y luego cuando cambia:

- El estado de movimiento: se informa en cuanto el programa detecta el cambio.
- El PWM aplicado: se limita la frecuencia del reporte a una vez cada 500 ms.
- La distancia en al menos 1 cm respecto al último valor impreso.
- La validez del sensor: pasa a «sin lectura» o se recupera.

Si los datos permanecen iguales, el monitor queda quieto. El bucle sigue leyendo el sensor aproximadamente cada 100 ms y atendiendo controles y paradas. Cambios pequeños de distancia pueden no imprimirse, pero sí se usan para decidir la parada a 20 cm o menos.

Una pulsación de dirección conserva la orden al soltar el botón, como antes. El pulsador rojo, un obstáculo, una lectura inválida o potencia cero detienen las salidas. Después de una parada automática se requiere una nueva pulsación de dirección.

## Lo que representa el montaje

Los botones son entradas de control; no sustituyen los motores. Los LED azules muestran IN1, IN2, IN3 e IN4; los verdes muestran ENA y ENB mediante PWM. La demostración verifica señales y decisiones del firmware, no fuerza, giro real ni desplazamiento de un carro.

En un vehículo físico se necesitan motores y un controlador adecuado. En este montaje Wokwi se usa su representación mediante LED. El catálogo estándar consultado no enumera motores DC ni L298N; los servos y motores paso a paso disponibles no son sustitutos directos para este código. Fuente: [hardware compatible con Wokwi](https://docs.wokwi.com/getting-started/supported-hardware).

La aceptación de esa representación como entrega de control de actuadores depende del criterio del docente; no se afirma que sea equivalente a probar motores.

## Comprobación

Se comprobó la sintaxis localmente. Esta corrección no se ejecutó directamente en Wokwi desde la sesión. Para verificarla: iniciar sin tocar controles, comprobar una sola línea de estado estable, pulsar avanzar, variar potencia, pulsar detener y cambiar la distancia a 10 cm durante una marcha. Las salidas deben detenerse aunque ya no haya reportes repetidos.
