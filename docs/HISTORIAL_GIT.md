# Evolución registrada en Git

Este documento describe los commits que ya existían antes de preparar la publicación en GitHub. No se cambiaron fechas ni se fabricaron etapas retrospectivas.

| Commit | Fecha | Cambio registrado |
|---|---|---|
| `11815f3` | 2026-10-29 | Alcance y arquitectura de la propuesta inicial. |
| `13cb7dc` | 2026-10-29 | Motores, sensor y reglas de parada. |
| `2810479` | 2026-10-29 | Comunicación MQTT, reconexión y heartbeat. |
| `42c98da` | 2026-10-29 | Herramientas de entorno y simulación inicial. |
| `4156c4a` | 2026-10-29 | Documentación y límites de validación. |
| `75a133c` | 2026-10-29 | Versión sencilla de Wokwi con pulsadores y potenciómetro. |
| `7d41d54` | 2026-11-02 | Variante de Wokwi con control remoto MQTT. |
| `873671c` | 2026-11-02 | Adaptación de la estructura de comunicación del ejemplo de clase. |
| `6488a02` | 2026-11-02 | Corrección del monitor serie en el montaje original con pulsadores. |

La entrega actual se concentra en `correccion_pulsadores/`. En la preparación para GitHub se reunieron sus módulos y diagrama, se añadió el enlace real de Wokwi proporcionado por el estudiante y se actualizó el README. Las otras variantes permanecen como parte del trabajo anterior.

Los commits muestran cambios guardados en sus fechas reales. No demuestran por sí solos pruebas físicas, ejecución en Wokwi ni el trabajo del estudiante en cada sesión del curso. Para sustentar, se debe explicar el código presentado y mostrar la simulación.

## Consultar el historial

Desde la carpeta raíz del repositorio:

```powershell
git log --oneline --reverse
git show --stat 75a133c
git show 6488a02 -- correccion_pulsadores/main.py
```

`git log` lista los cambios guardados; `git show` permite revisar qué cambió en un commit concreto. GitHub mostrará esos mismos commits cuando se suba la rama `main` completa, sin necesidad de volver a crearlos.
