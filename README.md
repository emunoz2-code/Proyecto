# Vehículo con ESP32 y MicroPython — Parcial 2

Firmware para controlar las señales de un vehículo mediante cinco pulsadores, regular el PWM con un potenciómetro y detenerse cuando el sensor ultrasónico detecta un obstáculo. El montaje se realiza en **Wokwi** y utiliza seis LED para representar las señales de dos motores.

**Entrega actual:** [código e instrucciones del montaje con pulsadores](correccion_pulsadores/README.md).

**Simulación:** [abrir el proyecto del estudiante en Wokwi](https://wokwi.com/projects/479614304886635521).

## Archivos para la sustentación

```text
correccion_pulsadores/
  main.py       Entradas, decisiones, control y monitor serie
  motores.py    Clase Motores: dirección y PWM
  sensor.py     Clase SensorDistancia: lectura del HC-SR04
  diagram.json  Componentes y conexiones de Wokwi
  README.md     Componentes, funcionamiento, ejecución y pruebas propuestas
  LEEME.md      Explicación de la corrección del monitor serie
```

Los cuatro archivos de ejecución deben estar juntos en la raíz del proyecto Wokwi. No se requieren instalaciones adicionales para ejecutar esta versión en el simulador.

## Componentes y funcionalidades

Se usan una ESP32, un HC-SR04, cinco pulsadores, un potenciómetro, seis LED y seis resistencias de 220 Ω. El programa permite avanzar, retroceder, girar y detener; controla ambas señales PWM entre 0 y 100 %; se detiene a 20 cm o menos, con lectura inválida, potencia cero o varios botones pulsados; y muestra los cambios de distancia, estado y PWM sin repetir un estado constante.

Los LED representan señales de control. El montaje no incluye un carro que se desplace, motores DC ni un L298N simulado. Las conexiones documentadas son para Wokwi.

## Organización y evolución

La carpeta `correccion_pulsadores/` es la entrega que corresponde al montaje explicado por el estudiante. `parcial2_wokwi/` conserva la variante MQTT, y `firmware/`, `simulation/`, `broker/` y las guías anteriores conservan la propuesta más amplia. Esos materiales se mantienen como antecedentes; no son necesarios para ejecutar el montaje con pulsadores ni constituyen el desarrollo de una aplicación de escritorio en esta entrega.

El historial mantiene los commits originales: [ver explicación de las etapas](docs/HISTORIAL_GIT.md). No se alteraron sus fechas. Cada modificación futura debe guardarse con un mensaje que describa el cambio realmente realizado.

## Requisitos del repositorio

| Requisito del Parcial 2 | Dónde se encuentra |
|---|---|
| Código fuente del firmware | Los tres archivos Python de `correccion_pulsadores/`. |
| Organización en módulos | Programa principal, clase de motores y clase del sensor. |
| README con descripción, componentes y funcionalidades | Este archivo y el README de la carpeta de entrega. |
| Evolución mediante commits | Historial Git completo y `docs/HISTORIAL_GIT.md`. |
| Enlace de Wokwi | Enlace de simulación al inicio de este README. |
| Archivos adicionales para reproducir el proyecto | `diagram.json` e instrucciones de ejecución. |

## Validación

Se comprueba localmente la sintaxis de los tres módulos y la correspondencia de los GPIO con el diagrama. La revisión con Python del computador no reemplaza la ejecución en MicroPython. El enlace de Wokwi fue proporcionado por el estudiante; su contenido actual no se ha comparado con los archivos locales. No se realizaron pruebas físicas. Las pruebas sugeridas para demostrar el funcionamiento están en el README de la entrega.

Para guardar y subir los siguientes cambios, consultar [la guía breve de Git y GitHub](docs/GITHUB.md).
