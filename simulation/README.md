# Simulación Wokwi del Parcial 2

**Estado:** archivos preparados; ejecución y enlace público pendientes. No se afirma que la simulación haya sido ejecutada.

La simulación conserva ESP32, HC-SR04, entrada de emergencia, PWM y dirección. Se usan LED para IN1–IN4 y ENA/ENB, y un analizador lógico para observar las seis señales. Esto es un modelo de entradas/salidas del firmware; no es una simulación eléctrica ni mecánica del L298N y los motores.

## Preparación

1. Desde la raíz del repositorio: `python tools/build_wokwi.py`.
2. Se generan `dist/wokwi/` y `dist/wokwi_parcial2.zip`. El exportador asigna una base MQTT aleatoria para reducir colisiones y no copia credenciales del montaje real.
3. Abrir [Wokwi MicroPython](https://wokwi.com/micropython) y elegir un proyecto **ESP32 MicroPython**. La plantilla debe corresponder a ESP32, no a Arduino/C++ ni a Pico.
4. Sustituir `diagram.json`, `main.py` y añadir los demás `.py` de `dist/wokwi/`, con esos nombres y todos en la raíz del proyecto de Wokwi. El ZIP es un paquete de intercambio; si la interfaz no ofrece importarlo directamente, añadir los archivos en el editor.
5. Usar el `config_local.py` generado, con `Wokwi-GUEST` y contraseña vacía. No pegar contraseñas reales en un proyecto público.
6. Iniciar y comprobar errores en el monitor serie. Si aparece emergencia física, colocar el interruptor en la posición que conecta el pin central a GND. El pin abierto representa pulsación/cable interrumpido.
7. Copiar la base MQTT impresa por el exportador y abrir la consola:

```powershell
& '.\.venv\Scripts\python.exe' tools/console.py --host test.mosquitto.org --user "" --base prog2/ID_GENERADO/carro01
```

`ID_GENERADO` debe reemplazarse por el valor real de `config_local.py`. El servicio público puede estar indisponible o limitar conexiones; no es infraestructura garantizada. [Servicio público Mosquitto](https://test.mosquitto.org/).

## Ensayos

- Ajustar la distancia del HC-SR04 a 100 cm; `status` debe mostrar un valor válido.
- Solicitar `move forward 30 2` y comparar LED/duty con la tabla de dirección.
- Cambiar distancia a 10 cm durante la maniobra; esperar parada y desarmado.
- Abrir el interruptor: se enclava la emergencia. Cerrar, ejecutar `clear`, esperar telemetría y pedir una maniobra nueva.
- Detener las renovaciones de movimiento y observar ENA/ENB en cero. Para capturar el timeout puro, enviar una sola orden con un cliente MQTT manual y no enviar `stop`.
- Descargar la traza del analizador lógico al detener la simulación y guardar evidencia, si la interfaz ofrece esa función.
- Guardar el proyecto, copiar su URL en `evidence/VALIDACION.md` y en README antes de entregar.

## Límites

El divisor de ECHO se dibuja para recordar la conexión física, pero Wokwi no certifica sus tensiones. El interruptor simulado representa solamente el contacto auxiliar; el corte de potencia de dos contactos está en el esquema físico. Los LED no reproducen carga inductiva ni corriente. No se debe conectar un carro físico al broker público usado aquí.

El gateway público de Wokwi permite conexión a servicios de Internet; normalmente no llega a la IP privada de Mosquitto en el computador. Para ensayar con el broker LAN se necesita una opción de gateway privado compatible y configurada según la documentación de Wokwi, o usar ESP32 física. [Red Wi-Fi en Wokwi](https://docs.wokwi.com/guides/esp32-wifi).

Los archivos se mantienen en formato de proyecto web; no se incluye `wokwi.toml` con rutas de binarios ficticias. Si se elige Wokwi para VS Code, habrá que preparar la imagen de firmware/filesystem que esa modalidad exige. [Guía MicroPython](https://docs.wokwi.com/guides/micropython).
