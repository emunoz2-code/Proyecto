# 5. Estrategia de pruebas y criterios de aceptación

## 5.1 Niveles de evidencia

| Nivel | Qué permite concluir | Qué no demuestra |
|---|---|---|
| Análisis de sintaxis | Archivos Python sin errores sintácticos en CPython | Existencia de periféricos o compatibilidad completa con la placa |
| Pruebas automatizadas PC | Reglas de seguridad y transporte ante entradas controladas | Tiempo real, red Wi-Fi real o motores |
| Wokwi | Ejecución MicroPython, sensor y señales digitales simuladas | Tensión, corriente, ruido, temperatura, inercia o protección analógica |
| Ensayo físico | Comportamiento medido del montaje específico | Seguridad universal de otras placas, fuentes o motores |

El registro `evidence/VALIDACION.md` distingue los niveles realmente ejecutados. La tabla física empieza sin datos; solo completarla con mediciones reales.

## 5.2 Pruebas automatizadas

Desde la raíz:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' tools/check_project.py
```

Se utilizan motores y sockets de prueba controlados por el programa. Son útiles porque permiten forzar fallos reproducibles: un mensaje partido en varios segmentos TCP, desconexión, duplicación de órdenes o ausencia de PINGRESP. No se presentan como conexión efectiva a Mosquitto.

## 5.3 Plan de aceptación en ESP32 o Wokwi

Para pruebas físicas, ruedas suspendidas al inicio y acceso inmediato al corte de potencia.

| ID | Procedimiento | Resultado esperado | Evidencia |
|---|---|---|---|
| P01 | Encender sin broker y sin órdenes | ENA=ENB=0; reintentos sin movimiento | Video/analizador |
| P02 | Medir a 10, 20, 50 y 100 cm, 10 muestras cada distancia | Valores plausibles; calcular error, dispersión y valores nulos | Tabla con regla |
| P03 | Enviar `move` sin `arm` | `not_armed`; motor deshabilitado | ack + salida |
| P04 | Armar y mover en cuatro direcciones | Tabla de señales correcta y sentidos verificados | Video + tabla |
| P05 | Cambiar PWM 20, 40, 60 % | Cambio de ciclo útil; corriente y giro documentados | Analizador/medidor |
| P06 | Emitir un solo `move`, mantener sensor válido, no renovar | Desarmado al alcanzar 600 ms lógicos; medir retraso real | EN y hora de última orden |
| P07 | Enviar heartbeats sin nuevos `move` | Misma parada P06; heartbeat no conserva marcha | Log + EN |
| P08 | Interrumpir Wi-Fi y, por separado, detener broker | Parada y posterior reconexión desarmada | Video/log |
| P09 | Acercar objeto a ≤20 cm durante marcha | Parada; retirar objeto no reanuda | Video |
| P10 | Desconectar ECHO sin tocar alimentación | Lectura inválida, parada y bloqueo de nuevas marchas | Telemetría |
| P11 | Pulsar emergencia física durante marcha | Vs retirado aun si software no responde; estado enclavado | Medida Vs y video |
| P12 | Liberar emergencia y enviar `arm` sin limpiar | Rechazado; `clear_estop` y nuevo `arm` necesarios | ack |
| P13 | Enviar JSON inválido, velocidad fuera de rango o secuencia repetida | Rechazo; no renovar plazos | ack |
| P14 | Almacenar un comando antiguo y reconectar | Retenido rechazado o sesión antigua inválida; no marcha | Log |
| P15 | Reiniciar ESP32 y broker | Ninguna reanudación de una orden previa | Video |
| P16 | Intentar credenciales y permisos incorrectos | Broker rechaza autenticación o publicación no autorizada | Log broker |
| P17 | Bloquear el programa en ensayo controlado, con ruedas elevadas | WDT reinicia; EN bajo al reiniciar; verificar tiempo real | Analizador |

P06–P08 deben medir la señal EN además del movimiento visual. Las ruedas pueden seguir por inercia; registrar tiempo de deshabilitación y tiempo de detención mecánica por separado. No probar sobre personas, animales, bordes o superficies de caída.

## 5.4 Tabla de dirección esperada

Con `INVERT_LEFT=False` e `INVERT_RIGHT=False`:

| Movimiento | IN1 | IN2 | IN3 | IN4 | ENA/ENB |
|---|---:|---:|---:|---:|---|
| Avance | 1 | 0 | 1 | 0 | PWM |
| Retroceso | 0 | 1 | 0 | 1 | PWM |
| Izquierda sobre su eje | 0 | 1 | 1 | 0 | PWM |
| Derecha sobre su eje | 1 | 0 | 0 | 1 | PWM |
| Parada | 0 | 0 | 0 | 0 | 0 |

Los motores montados en espejo pueden exigir invertir uno; corroborar sobre el chasis real. Al cambiar dirección se deshabilita el puente durante la transición; esa pausa de 100 µs es eléctrica, no espera a que el motor deje de girar. Ensayar inversiones a baja velocidad y considerar rampa y pausa mecánica en una mejora posterior.

## 5.5 Criterios académicos propuestos

- Demostrar todos los estados y salidas relevantes sin movimiento inesperado.
- Documentar error del sensor y justificar el umbral; como objetivo inicial de laboratorio, error absoluto ≤2 cm entre 10 y 100 cm sobre superficie plana, sujeto a condiciones y ficha real.
- Obtener telemetría cercana a 2 Hz y heartbeat a 1 Hz en red estable; documentar pérdidas y latencias observadas.
- Confirmar repetición de comandos cada 200 ms y corte por falta de renovación; no afirmar una latencia medida sin registro.
- Entregar fuente, configuración sin secretos, enlace del repositorio e historial real.
- Si se elige Wokwi, guardar URL, versión de archivos y capturas de la ejecución.

Estos criterios son metas de aceptación propuestas para el proyecto; no reemplazan criterios numéricos del docente que no fueron proporcionados.
