# 7. Base diseñada para la aplicación de escritorio del Parcial 3

El Parcial 2 entrega el contrato MQTT y una consola funcional de ensayo. La interfaz gráfica completa pertenece al siguiente parcial y no se presenta como implementada.

## Arquitectura propuesta

```text
app_desktop/
  main.py               arranque y configuración
  ui/main_window.py     botones, estado, distancia y gráficas
  mqtt_service.py       Paho MQTT, suscripciones y reconexión
  controller.py         sesión, secuencia, armado y renovación de órdenes
  models.py             validación de telemetría y estados
  storage.py            registro CSV o SQLite con hora de recepción
  settings.py           host y base; secretos fuera del repositorio
```

Puede emplearse Tkinter (incluido habitualmente en Python de escritorio) o PySide, según los requisitos del siguiente parcial. La elección gráfica no cambia el protocolo. `tools/console.py` muestra cómo conectar Paho 2.x, recibir estados y enviar comandos, aunque su interacción de texto no constituye una GUI.

## Pantalla prevista

```text
┌ Vehículo MQTT ──────────────────────────────────────────┐
│ Broker ●  ESP32 ●  Datos: hace 0.2 s  Estado: DESARMADO  │
│ Sesión actual       [Armar] [Liberar emergencia]         │
│                   [ Avanzar ]                          │
│ [ Izquierda ]     [ DETENER ]     [ Derecha ]            │
│                   [ Retroceder ]                       │
│ PWM solicitado: 30 % ──────●────────   [EMERGENCIA]      │
│ Distancia: 78.4 cm | Sensor válido | Batería: no medida  │
│ Gráfica de distancia / tabla de comandos y alertas      │
└────────────────────────────────────────────────────────┘
```

## Reglas de interacción

1. Deshabilitar movimiento hasta disponer de telemetría reciente, sesión actual y ausencia de emergencia. Un `online=true` retenido no basta.
2. Armado explícito del operador. Mantener movimiento solamente mientras se presiona el control; renovar cada 200 ms con una nueva secuencia.
3. Al soltar, perder foco, cerrar ventana o perder conexión: cancelar el temporizador de marcha y publicar `stop` si es posible. Nunca rearmar automáticamente al volver a la ventana o reconectar.
4. Un heartbeat cada 250 ms puede conservar el armado, pero no sustituye los comandos de movimiento.
5. Si no llega confirmación o el dato queda antiguo, marcar estado incierto y cancelar órdenes. El firmware aplica su propio timeout aunque la GUI falle.
6. Mostrar `sensor_ok=false` como dato no disponible, no como distancia cero. Mostrar PWM como porcentaje de mando, no velocidad real.
7. Mantener emergencia visible y separada del cierre normal. `clear_estop` solo libera el enclavamiento; nuevo armado obligatorio.
8. Si cambia `session`, borrar la secuencia local y cancelar la maniobra. No volver a enviar órdenes guardadas.

## Concurrencia y almacenamiento

Paho puede usar un hilo para la red. Sus callbacks no deben modificar directamente widgets de Tkinter: colocar eventos en una cola y procesarla con `after`. En PySide, usar señales y slots. El temporizador de movimiento pertenece al controlador de la aplicación, no al hilo de dibujo de la gráfica.

Guardar: fecha/hora de recepción del PC, contador de la ESP32, sesión, secuencia, topic, comando, ack, distancia, validez y motivo de parada. Limitar el tamaño de la gráfica y del registro en memoria. Conservar JSON originales cuando sirvan como evidencia, sin contraseñas.

## Ampliaciones deliberadamente pendientes

- Medición de batería: divisor y protección dimensionados según tensión máxima real, canal ADC1, calibración y filtrado. Mantener `battery_v=null` hasta implementarla.
- Encoders: velocidad real, distancia recorrida y control de lazo cerrado.
- Rampa de aceleración e inversión condicionada por detención mecánica.
- Sensores laterales/traseros para una asistencia de movimiento más completa.
- TLS, validación de certificado y mejoras de sesión/control si se requiere operar fuera de la LAN.

La interfaz futura no debe debilitar las verificaciones locales del firmware para conseguir una demostración más fluida.
