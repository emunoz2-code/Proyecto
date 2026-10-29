# 4. Contrato MQTT, estados y recuperación

## 4.1 Nombres y direcciones

Base predeterminada `prog2/equipo01/carro01`. Cambiar equipo/vehículo de forma coherente en ESP32, broker ACL y cliente. Un identificador de cliente MQTT único evita que dos placas se expulsen; la ESP32 añade su identificador físico al nombre de dispositivo.

| Topic relativo a la base | Publica → recibe | Periodicidad | QoS / retain |
|---|---|---|---|
| `/cmd` | PC → ESP32 | Evento; renovar movimiento cada 200 ms | 0 / false |
| `/ack` | ESP32 → PC | Una respuesta por comando recibido | 0 / false |
| `/telemetry` | ESP32 → PC | Cada 500 ms | 0 / false |
| `/heartbeat` | ESP32 → PC | Cada 1000 ms | 0 / false |
| `/availability` | ESP32/broker → PC | Conexión y última voluntad | 0 / true |

El cliente solicita QoS 0 y `clean session=true`: se descartan órdenes pendientes de sesiones anteriores. QoS 0 puede perder mensajes, por eso hay confirmación de aplicación, renovación de marcha y parada local. No se usa QoS 1 para órdenes, pues este transporte no lo implementa. [Especificación MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html).

## 4.2 Comandos JSON (versión 1)

`session` se lee en la telemetría actual. Los siguientes son ejemplos; sustituir el texto `SESION_ACTUAL` por el valor real. `seq` es un entero estrictamente creciente dentro de esa sesión; no usar `true`, decimales ni cadenas. Solo debe existir un operador activo por vehículo.

```json
{"v":1,"action":"arm","session":"SESION_ACTUAL","seq":1}
```

```json
{"v":1,"action":"move","session":"SESION_ACTUAL","seq":2,"direction":"forward","speed":30}
```

Direcciones admitidas: `forward`, `backward`, `left`, `right`. El porcentaje válido para movimiento es 1 a `MAX_SPEED` (60 inicialmente); usar `stop` para cero. Cambiar velocidad consiste en emitir un nuevo `move` con nueva secuencia y porcentaje, no en cambiar un valor sin autorización de marcha.

```json
{"v":1,"action":"heartbeat","session":"SESION_ACTUAL","seq":3}
```

Este heartbeat PC → ESP32 mantiene el estado armado en reposo hasta el límite de control, pero no renueva la marcha. La consola de ensayo usa movimientos acotados y no mantiene el armado indefinidamente mientras se escribe.

```json
{"v":1,"action":"stop"}
```

```json
{"v":1,"action":"estop"}
```

Se aceptan `stop` y `estop` sin conocer sesión/secuencia para favorecer la detención. `stop` desarma; `estop` también enclava el bloqueo. Ambas órdenes requieren JSON válido y no retenido. Para liberar el bloqueo:

```json
{"v":1,"action":"clear_estop","session":"SESION_ACTUAL","seq":4}
```

Requiere el contacto NC físico cerrado y solo deja el carro desarmado. Después hay que esperar la nueva sesión, enviar `arm` y una nueva orden `move`. Se rechazan propiedades desconocidas, versiones distintas, secuencias duplicadas y payloads mayores de 384 bytes.

## 4.3 Respuestas y telemetría

```json
{"v":1,"ok":true,"reason":"move","seq":2,"session":"0123456789abcdef"}
```

La confirmación significa que el firmware aceptó la orden y actualizó las salidas; no demuestra que las ruedas efectivamente giraron. El vehículo no tiene encoders.

```json
{
  "v":1,"session":"0123456789abcdef","seq":2,"uptime_ms":12500,
  "connected":true,"armed":true,"estop":false,"physical_estop":false,
  "direction":"forward","speed_pct":30,"distance_cm":78.4,
  "sensor_ok":true,"reason":"moving","battery_v":null
}
```

`distance_cm=null` indica una adquisición inválida. `sensor_ok` también es falso cuando la lectura tiene al menos 350 ms de antigüedad. `uptime_ms` usa el contador de MicroPython, que puede volver al inicio al reiniciar y dar la vuelta; el PC no debe tratarlo como fecha UTC. Debe guardar además la hora local de recepción y calcular antigüedad con su reloj monotónico.

Heartbeat ESP32 → PC: `{"v":1,"seq":12,"uptime_ms":12500}`. Disponibilidad: `{"v":1,"online":true}` o `false`. La última voluntad se registra al conectar y el broker la emite al detectar una salida inesperada. El keepalive es 10 s y el cliente comprueba PINGRESP; **la voluntad no sustituye el timeout de 600 ms del motor**. Un estado retenido `online=true` tampoco demuestra presencia actual: la interfaz debe revisar telemetría reciente.

## 4.4 Condiciones de parada

| Condición | Acción |
|---|---|
| 600 ms sin nuevo `move` válido | EN=0, desarmar, nueva sesión |
| 1000 ms sin control válido estando armado | Desarmar |
| Distancia ≤20 cm o medida inválida/antigua | Desarmar; no reanudar al despejar |
| Contacto NC abierto | Corte físico de Vs y bloqueo de software |
| `estop` remoto | Deshabilitar y enclavar; depende de que llegue el mensaje |
| Pérdida Wi-Fi/TCP, error de protocolo o cola llena | Detener y reconectar desarmado |
| Excepción no recuperada o Ctrl+C | `finally` deshabilita motores; WDT puede reiniciar |
| Bloqueo del intérprete | WDT de 5 s como respaldo; corte físico disponible |

El plazo de 600 ms es una regla lógica medida desde el último comando aceptado, **no un máximo certificado de detención mecánica**. En operación normal se añade el retraso de ejecución del ciclo y la inercia. `time_pulse_us` puede esperar en dos fases, cada una acotada por 25 ms. Se debe medir la latencia en hardware con ENA/ENB y registrar el resultado. No hay garantía de tiempo real duro en MicroPython.

## 4.5 Reconexión y alcance del transporte

1. Desarmar antes de cualquier DNS, conexión TCP o Wi-Fi.
2. Conectar Wi-Fi con espera limitada y atender la entrada de emergencia mientras se espera.
3. Abrir MQTT, registrar última voluntad y suscribirse; solo aceptar control operativo después de SUBACK.
4. Crear nueva sesión, publicar disponibilidad y telemetría. No recuperar velocidad anterior.
5. Ante error, cerrar socket, detener y esperar 0.5, 1, 2, 4, 8 y hasta 10 s. Restablecer espera corta tras 10 s estables.

`mqtt_wire.py` es un cliente educativo limitado: MQTT 3.1.1, una suscripción QoS 0, usuario/contraseña, voluntad, ping y publicación. Durante marcha usa socket no bloqueante, lectura máxima de 256 bytes por ciclo, hasta cuatro paquetes por ciclo, paquete de hasta 1024 bytes y cola de hasta 4096 bytes. Fragmentos incompletos caducan a los 500 ms y envíos detenidos a los 1000 ms. DNS y conexión se realizan únicamente parado; el watchdog es respaldo si la plataforma se bloquea allí.

La sesión aleatoria y secuencias reducen repetición accidental y órdenes antiguas; **no son autenticación criptográfica**. Rotan en reconexión y desarmado. Las banderas de retención se rechazan al recibirlas; además, la sesión impide reutilizar órdenes retenidas de una conexión anterior. Un broker puede entregar una publicación en vivo con RETAIN desactivado aunque el emisor la haya almacenado; por eso el emisor siempre debe usar `retain=false` y no se confía solamente en esa bandera.

Esta entrega supone un único operador y red local confiable. La evolución a Internet exige TLS con validación de certificados, control de acceso revisado y una implementación compatible; cambiar solamente el puerto a 8883 no activa TLS.
