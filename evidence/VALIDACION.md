# Registro de validación de la entrega

Fecha de preparación: **29 de octubre de 2026**, zona America/Bogota.

## Ejecutado en este computador

| Comprobación | Resultado |
|---|---|
| Entorno Python del proyecto | `.venv`, Python 3.14.7 |
| Dependencias PC | Paho MQTT 2.1.0, mpremote 1.29.0, esptool 5.6.0; versiones completas en `requirements-lock.txt` |
| Compatibilidad de dependencias (`pip check`) | Sin dependencias rotas |
| Pruebas automatizadas | **42 pruebas aprobadas**: control, reloj, adaptadores y transporte MQTT con dobles de prueba |
| Sintaxis Python | Analizada con AST de CPython; ver salida reproducible en `comprobaciones.txt` |
| JSON Wokwi | Analizado; identificadores únicos y referencias a componentes existentes |
| Esquemas | SVG generados, renderizados a PNG e inspeccionados visualmente |
| Cliente de consola | Importación y `--help` comprobados; sin conexión real a broker |
| Git | Repositorio local, rama `main`, commits reales por etapas de esta sesión |
| PyCharm | Instalación existente detectada; entorno y configuración `.run` preparados |
| Puertos serie | Solo se identificaron COM6/7/8 como puertos Bluetooth; no se identificó ESP32 por USB |

Los 42 casos incluyen: armado obligatorio, cuatro direcciones, pérdida de renovación incluso con heartbeat, secuencias duplicadas, sesión antigua, entrada inválida, límite de PWM, sensor inválido/antiguo, obstáculo, emergencia enclavada, vuelta del contador de tiempo, formato CONNECT/Will/SUBACK, fragmentación TCP, envíos parciales, rechazo del broker, colas acotadas y tiempos de espera de red.

## Pendiente: no presentar como realizado

- Ejecución del firmware con MicroPython en ESP32 o Wokwi.
- Medición de tensiones, corriente, temperatura, distancia real y detención.
- Interoperabilidad completa con un Mosquitto real, autenticación y permisos ACL.
- Prueba de Wi-Fi, desconexión y watchdog en la placa.
- Apertura y selección final del intérprete en la interfaz de PyCharm.
- Publicación en GitHub y creación/guardado de URL Wokwi.

**URL GitHub:** pendiente de crear/publicar en la cuenta elegida.

**URL Wokwi:** pendiente de crear, ejecutar y guardar.

Las pruebas PC utilizan entradas controladas y sustitutos de los periféricos/sockets. No validan un L298N físico ni demuestran que MicroPython tenga exactamente el mismo comportamiento que CPython. El firmware se entrega como implementación preparada y comprobada a ese nivel, con un plan explícito de aceptación para hardware o simulación.

## Historial y uso académico

El repositorio registra etapas reales: alcance; control y montaje; integración MQTT; entorno y simulación; validación y documentación final. Es trabajo preparado en esta sesión. No se modificaron fechas para aparentar trabajo de días o semanas anteriores. El estudiante debe revisar, ejecutar, comprender y continuar el desarrollo, incluyendo resultados reales y correcciones en nuevos commits.

Consultar `git log --oneline --reverse` para el historial actualizado. El paquete ZIP incluye una copia portable del historial Git (`historial.bundle`), pero no el entorno instalado ni credenciales. Para obtener un repositorio con ese historial desde el ZIP: `git clone historial.bundle vehiculo-mqtt`.
