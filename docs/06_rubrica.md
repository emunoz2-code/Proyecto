# 6. Correspondencia con el enunciado del Parcial 2

El texto proporcionado contiene requisitos, pero no niveles de desempeño ni porcentajes. Esta matriz es una correspondencia verificable con ese enunciado; no atribuye puntajes inventados.

| Requisito del enunciado | Entregable | Evidencia y cierre pendiente |
|---|---|---|
| Firmware MicroPython sobre ESP32 | `firmware/*.py`, instrucciones de carga | Sintaxis y pruebas PC; falta ejecución en ESP32 o Wokwi |
| Lectura de sensores | `ultrasonic.py`, telemetría y validez | Casos simulados de entrada; falta contrastar distancia real |
| Manejo de entradas/salidas y actuadores | `motor.py`, GPIO33, pinout | Pruebas con dobles de periféricos; falta giro, consumo y corte físico |
| Procesamiento de información | `control.py`, validación, estados y umbral | Pruebas de secuencias, timeout, emergencia y medidas inválidas |
| Organización de módulos | Arquitectura, firmware separado de herramientas PC | Árbol y responsabilidades en README y guía |
| README: descripción, componentes y funciones | `README.md` | Documento editable incluido |
| Repositorio en GitHub | Repositorio Git local e instrucciones de publicación | Falta URL y push a la cuenta del estudiante |
| Evolución mediante commits claros | Historial local por etapas reales | Continuar commits con pruebas y correcciones reales del curso |
| Enlace Wokwi si se utiliza | `simulation/`, paquete exportable | Falta crear/guardar/ejecutar la simulación y registrar su URL |
| Archivos para comprender y ejecutar | Guías, Mosquitto, herramientas y pruebas | Archivos incluidos y registro de comprobaciones |

## Evidencias que deben acompañar la entrega final

- URL del repositorio y captura del historial que muestre progreso real.
- Captura o video de ESP32/Wokwi leyendo distancia y controlando salidas.
- Registro de pérdida de comandos, pérdida de broker y emergencia.
- Tabla física diligenciada cuando corresponda; nunca presentar valores propuestos como medidos.
- URL de Wokwi si esa es la modalidad seleccionada.

## Guion sugerido de sustentación (8–10 minutos)

1. Problema, objetivos y arquitectura (1 min).
2. Pinout, divisor ECHO y separación de alimentación (2 min).
3. Módulos y contrato MQTT (2 min).
4. Demostración de distancia, movimiento y paradas (3 min).
5. Historial, limitaciones y evolución al Parcial 3 (1–2 min).
