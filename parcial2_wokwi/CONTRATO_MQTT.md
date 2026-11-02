# Comunicación preparada para la aplicación del Parcial 3

Este documento define cómo utilizar el firmware del Parcial 2. La aplicación gráfica todavía no está desarrollada. No hay que cambiar el montaje para incorporarla después.

## Conexión

- Broker: `test.mosquitto.org`, puerto TCP `1883`, sin usuario ni contraseña.
- ESP32 y aplicación usan identificadores de cliente diferentes.
- Base de topics: `parcial2/vehiculo_7d49c2a1`, configurable en `config.py`.
- Formato JSON UTF-8, versión `v: 1`, QoS 0.
- Todos los comandos: **retain=false**. No publicar comandos retenidos.
- Una sola aplicación controla cada vehículo. El sufijo evita coincidencias accidentales; no es una contraseña.

El broker es público y no cifra esta conexión. Usarlo solamente para la demostración virtual, sin datos privados. Otros usuarios pueden leer o publicar en sus topics; la sesión no proporciona autenticación. No trasladar esta configuración directamente a un vehículo físico.

## Topics

En la tabla, `BASE` significa el valor de `TOPIC_BASE`.

| Topic | Emisor → receptor | Contenido |
|---|---|---|
| `BASE/cmd` | Aplicación → ESP32 | Órdenes de control |
| `BASE/ack` | ESP32 → aplicación | Aceptación o rechazo de cada orden |
| `BASE/telemetry` | ESP32 → aplicación | Distancia, dirección, PWM y estado; cada 500 ms y tras comandos |
| `BASE/heartbeat` | ESP32 → aplicación | Señal de funcionamiento cada 1000 ms |
| `BASE/availability` | ESP32/broker → aplicación | `{"v":1,"online":true}` o `false`; único topic retenido |

El mensaje `online:false` es el último testamento MQTT: el broker lo emite al detectar la pérdida de conexión. Puede tardar. La app debe tratar la telemetría con más de 2 s sin actualizar como **estado desconocido**, desactivar el movimiento y cancelar los envíos periódicos, incluso si availability conserva `true`. No mostrar como actual la última distancia recibida indefinidamente.

## Sesión y secuencia

Antes de controlar, leer `session` y `seq` de la telemetría actual. `session` es un identificador aleatorio que cambia al detener/deshabilitar el control, tras una emergencia o al reconectar. `seq` debe ser entero creciente, entre 0 y 2147483647; usar el último valor confirmado más uno (o 0 al iniciar una sesión).

Cada envío nuevo, incluida la repetición del movimiento, lleva un `seq` distinto. La ESP32 rechaza sesiones antiguas, secuencias repetidas, campos desconocidos y comandos que llegan marcados como retenidos. No se debe reintentar automáticamente una orden rechazada utilizando una sesión nueva.

## Órdenes

Reemplazar `SESION_ACTUAL` por el valor recibido. Los ejemplos de secuencia son ilustrativos.

**Habilitar el control (sin mover):**

```json
{"v":1,"action":"arm","session":"SESION_ACTUAL","seq":0}
```

Solo se acepta con conexión activa, sensor válido y reciente, distancia mayor de 20 cm y sin emergencia. Esperar `ack.ok=true` antes de mover.

**Mover:**

```json
{"v":1,"action":"move","session":"SESION_ACTUAL","seq":1,"direction":"forward","speed":50}
```

| `direction` | Movimiento | LED de dirección |
|---|---|---|
| `forward` | Avanzar | IN1 e IN3 |
| `backward` | Retroceder | IN2 e IN4 |
| `left` | Girar a la izquierda | IN2 e IN3 |
| `right` | Girar a la derecha | IN1 e IN4 |

`speed` es un entero de 1 a 100, porcentaje PWM, no velocidad medida. Para cero usar `stop`. Repetir `move` cada **250 ms mientras el usuario mantenga pulsado el control**, incrementando `seq`. Sin una nueva orden de movimiento durante **800 ms**, el firmware detiene y cambia de sesión. Un heartbeat por sí solo NO mantiene el movimiento.

**Mantener habilitado el control estando detenido:**

```json
{"v":1,"action":"heartbeat","session":"SESION_ACTUAL","seq":2}
```

Enviar cada 500 ms si se mantiene el estado habilitado sin movimiento. Sin órdenes válidas durante 1500 ms se deshabilita. Este comando no habilita ni inicia movimiento. No confundirlo con `BASE/heartbeat`, que es la señal enviada por la ESP32.

**Detener al soltar el botón o perder el foco de la ventana:**

```json
{"v":1,"action":"stop"}
```

Apaga todas las salidas y deshabilita el control. Para un nuevo movimiento se necesita una nueva acción del usuario, la sesión vigente y otro `arm`.

**Emergencia remota:**

```json
{"v":1,"action":"estop"}
```

Detiene y deja la emergencia bloqueada. El pulsador rojo local provoca el mismo bloqueo. Soltarlo no reanuda el control.

**Restablecer después de una emergencia:**

```json
{"v":1,"action":"clear_estop","session":"SESION_ACTUAL","seq":0}
```

Solo se acepta si el pulsador local está suelto. Cambia la sesión y mantiene el vehículo detenido. Luego leer la nueva sesión, enviar `arm` y esperar confirmación. `arm` vuelve a verificar el obstáculo y el sensor.

Por seguridad de parada, `stop` y `estop` no requieren sesión ni secuencia; siguen exigiendo JSON válido, `v:1`, campos admitidos y mensaje no retenido. No energizan salidas.

## Respuestas y datos de la interfaz

Ejemplo de confirmación (también se envía ante rechazo):

```json
{"v":1,"ok":true,"reason":"move","seq":1,"session":"SESION_ACTUAL"}
```

Ejemplo de telemetría durante una orden:

```json
{
  "v": 1, "session": "SESION_ACTUAL", "seq": 1,
  "uptime_ms": 3200, "connected": true, "armed": true,
  "estop": false, "physical_estop": false,
  "direction": "forward", "speed_pct": 50,
  "distance_cm": 100.0, "sensor_ok": true, "reason": "moving"
}
```

`uptime_ms` procede del reloj de la placa y puede desbordarse; no es fecha/hora. La app usa su propio reloj para medir cuánto lleva sin recibir datos. `speed_pct` es la salida aplicada: cero al detener. `sensor_ok` indica una medición válida y reciente, no que el camino esté libre. Para eso también hay que comprobar `distance_cm > 20`.

Motivos frecuentes: `obstacle` (obstáculo), `sensor_invalid` (lectura fallida), `sensor_stale` (lectura caducada), `move_timeout` (no se renovó movimiento), `control_timeout` (control sin actividad), `physical_estop` (pulsador rojo), `disconnected` (sin enlace), `session_invalid` (sesión antigua), `sequence_invalid` (secuencia inválida).

## Comportamiento previsto para el Parcial 3

La interfaz necesitará botones de dirección, un ajuste de potencia, parada, restablecimiento y panel de distancia/conexión. Para cada nueva pulsación: obtener sesión actual, habilitar con `arm`, esperar confirmación y repetir `move` mientras se mantenga pulsado. Un ajuste del deslizador durante la marcha cambia `speed` del siguiente envío; estando detenido no inicia marcha.

Al soltar, salir de la ventana o perder conexión: cancelar el temporizador y enviar `stop` si el enlace está disponible. Si cambia `session` o aparece un rechazo, cancelar el movimiento y exigir una nueva acción explícita del usuario. Nunca cambiar automáticamente a la sesión nueva para continuar una marcha anterior. El firmware comprueba obstáculos y emergencias independientemente de la interfaz.

## Prueba previa a la aplicación

Con cualquier cliente MQTT de pruebas, suscribirse a `BASE/#`, con QoS 0. Ejecutar Wokwi y comprobar telemetría. Para verificar un movimiento sin interfaz, programar el cliente para enviar `arm` y, tras recibir confirmación, `move` en menos de 1,5 s; si se hace manualmente, se puede mantener primero `heartbeat` cada 500 ms. Un solo `move` muestra una salida breve y se detiene al cumplirse 800 ms: es el comportamiento esperado. No aumentar los plazos para simular una orden mantenida.

## Referencias

- [Wi-Fi y MQTT en Wokwi](https://docs.wokwi.com/guides/esp32-wifi).
- [Broker de pruebas Mosquitto](https://test.mosquitto.org/).
- [Sockets en MicroPython](https://docs.micropython.org/en/latest/library/socket.html).
