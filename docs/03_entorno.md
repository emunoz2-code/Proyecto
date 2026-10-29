# 3. Entorno Windows, PyCharm, MicroPython y GitHub

## 3.1 Estado encontrado en este equipo

El 29 de octubre de 2026 se detectaron Git 2.45.1, PyCharm 2026.2.2 y Python 3.14.7 instalado en `C:\Users\em435\AppData\Local\Programs\Python\Python314\python.exe`. El comando `python` del sistema apunta a otra instalación (MSYS2 3.12.12), mientras que `py -0p` no detectó intérpretes. Para evitar ambigüedad se creó `.venv` con el ejecutable explícito de Python 3.14.7.

Se conservó la identidad Git que ya estaba configurada; no se cambió la configuración global ni se inventó una cuenta. PyCharm ya existe: no fue necesario reinstalarlo. Se incluye una configuración de ejecución en `.run/`; falta abrirla en la interfaz y confirmar su selección de intérprete.

## 3.2 Instalación en otro computador

1. Descargar Git desde [Git para Windows](https://git-scm.com/install/windows). Conservar Git Credential Manager y la integración con la terminal. Verificar `git --version`.
2. Instalar Python desde [Python para Windows](https://www.python.org/downloads/windows/). Seleccionar una versión compatible con las dependencias y anotar la ruta al ejecutable.
3. Instalar PyCharm desde [JetBrains](https://www.jetbrains.com/help/pycharm/installation-guide.html). La edición unificada conserva funciones esenciales gratuitas; este proyecto no necesita funciones Pro.
4. Instalar Mosquitto únicamente si se usará broker local; seguir `broker/README.md`.

Desde PowerShell, ubicarse en la carpeta del proyecto. En el equipo actual:

```powershell
Set-Location 'C:\Users\em435\OneDrive\Documentos\ChatGPT\MQTT Proyecto'
& 'C:\Users\em435\AppData\Local\Programs\Python\Python314\python.exe' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-dev.txt
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' tools/check_project.py
```

El entorno ya creado no necesita recrearse. En otro computador, sustituir la primera ruta Python. No es necesario activar PowerShell ni cambiar su política de ejecución para usar directamente `.venv\Scripts\python.exe`.

`requirements-dev.txt` describe rangos admitidos; `requirements-lock.txt` registra las versiones instaladas en esta sesión. El entorno PC ejecuta herramientas y pruebas. El firmware se ejecuta en **MicroPython dentro de la ESP32**, con sus módulos `machine` y `network`.

## 3.3 Configuración de PyCharm

1. **File → Open**: abrir la carpeta `MQTT Proyecto` completa.
2. **Settings → Python → Interpreter → Add Local Interpreter**: seleccionar el entorno existente `.venv\Scripts\python.exe`.
3. **Settings → Version Control → Git**: verificar `C:\Program Files\Git\cmd\git.exe` y pulsar Test.
4. En configuraciones de ejecución, seleccionar **Pruebas del proyecto**. Si la configuración compartida no aparece por diferencias de versión, crear una configuración Python con módulo `unittest`, parámetros `discover -s tests -v` y directorio de trabajo la raíz.
5. Ejecutar las pruebas. Para la consola, crear otra configuración con script `tools/console.py` y parámetros `--host IP_DEL_BROKER --base prog2/equipo01/carro01`.
6. Crear `firmware/config_local.py` copiando el ejemplo. El archivo se excluye de Git.

PyCharm es editor y entorno de herramientas PC. No pulsar Run sobre `firmware/main.py`: Python del computador no controla los GPIO. No se depende de un complemento MicroPython de PyCharm; la transferencia se hace con la herramienta oficial `mpremote`. [Intérpretes de PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html), [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html).

## 3.4 Instalar MicroPython en la ESP32

**Alimentación de motores físicamente desconectada durante borrado y programación.** Identificar el puerto COM en el Administrador de dispositivos o mediante:

```powershell
& '.\.venv\Scripts\python.exe' -m serial.tools.list_ports
```

Descargar una versión estable desde [ESP32_GENERIC para WROOM](https://micropython.org/download/ESP32_GENERIC/). Guardar el nombre exacto y la versión utilizada en la evidencia. No usar firmware C3/S3 para ESP32 clásica.

Ejemplo para **ESP32 clásica** y esptool 5; cambiar `COM5` y el nombre del archivo. El primer comando borra todos los archivos existentes en esa placa:

```powershell
& '.\.venv\Scripts\python.exe' -m esptool --chip esp32 --port COM5 erase-flash
& '.\.venv\Scripts\python.exe' -m esptool --chip esp32 --port COM5 --baud 460800 write-flash 0x1000 '.\ESP32_GENERIC-VERSION.bin'
```

El desplazamiento corresponde a la placa clásica y debe confirmarse en la página de descarga del archivo concreto. Si no conecta, cerrar otras consolas serie, verificar cable de datos, bajar baud a 115200 y seguir el procedimiento BOOT/EN de la placa. No cambiar pines de arranque al azar.

## 3.5 Configurar Wi-Fi y cargar archivos

```powershell
Copy-Item -LiteralPath '.\firmware\config_local.example.py' -Destination '.\firmware\config_local.py'
```

Editar los siguientes valores:

| Valor | Contenido |
|---|---|
| `WIFI_SSID`, `WIFI_PASSWORD` | Red 2.4 GHz y contraseña |
| `MQTT_HOST` | IPv4 LAN del computador con Mosquitto |
| `MQTT_PORT` | 1883 en la red de laboratorio |
| `MQTT_USER`, `MQTT_PASSWORD` | Usuario `carro` y contraseña del broker |
| `TOPIC_ROOT`, `DEVICE_ID` | Coincidir exactamente con ACL y cliente |

En ESP32, `localhost` sería la propia ESP32. Wi-Fi de invitado o aislamiento entre clientes puede impedir conexión al PC aunque ambos tengan Internet.

Con motores desconectados, ejecutar desde PowerShell:

```powershell
.\tools\upload.ps1 -Port COM5
& '.\.venv\Scripts\python.exe' -m mpremote connect COM5 reset
& '.\.venv\Scripts\python.exe' -m mpremote connect COM5 repl
```

Si la política local impide ejecutar scripts PowerShell, copiar manualmente cada módulo con `mpremote connect COM5 fs cp RUTA :NOMBRE.py`, incluido `config_local.py`, y copiar `main.py` al final. No cambiar políticas globales para solucionar este paso.

No ejecutar la carga si ya existe código ajeno que deba preservarse: respaldar antes con `mpremote fs cp`. Esta entrega no ha borrado ni programado una placa.

Al reiniciar debe verse conexión Wi-Fi/MQTT o un mensaje de reintento, nunca un movimiento espontáneo. El WDT puede reiniciar después de Ctrl+C; para mantenimiento conservar motores sin alimentación.

## 3.6 Uso del cliente de ensayo

En otra terminal, desde la raíz:

```powershell
& '.\.venv\Scripts\python.exe' tools/console.py --host 192.168.1.10 --base prog2/equipo01/carro01 --user operador
```

Introducir la contraseña cuando se solicite. Esperar aproximadamente un segundo y escribir `status`. Una prueba explícita es `move forward 30 2`: arma y solicita avance al 30 % durante 2 s, con renovación periódica, confirmaciones y orden final de parada. El porcentaje es **PWM configurado**, no velocidad medida en m/s. Empezar con ruedas elevadas; un motor puede no arrancar a bajo PWM.

`estop` enclava la emergencia; `clear` la libera solo si el contacto físico está cerrado. Esperar nueva telemetría y dar una nueva orden de movimiento. `stop` y `quit` solicitan detención. Si la conexión desaparece, el timeout de la placa es la defensa principal; una orden de parada por red podría no llegar.

## 3.7 Historial Git y publicación en GitHub

La carpeta contiene un repositorio local en rama `main`. Revisar:

```powershell
git status
git log --oneline --reverse
git config --get user.name
git config --get user.email
```

Para un equipo nuevo sin identidad, establecerla únicamente después de sustituir los ejemplos por datos propios:

```powershell
git config user.name 'TU NOMBRE'
git config user.email 'TU CORREO O CORREO PRIVADO DE GITHUB'
```

1. Iniciar sesión en GitHub y crear un repositorio, por ejemplo `vehiculo-mqtt-parcial2`. Elegir visibilidad y crear vacío, sin README adicional, porque ya existe uno local.
2. Antes de publicar, comprobar `git status`, revisar archivos y verificar que contraseñas y `.venv` no estén incluidos. El historial usa la identidad preexistente; revisar también el correo de autor que se publicará.
3. Copiar la URL HTTPS del repositorio y ejecutar, sustituyendo el marcador:

```powershell
git remote add origin https://github.com/TU_USUARIO/vehiculo-mqtt-parcial2.git
git push -u origin main
```

Si `origin` ya existe, consultar `git remote -v` y verificarlo antes de cambiarlo. Git Credential Manager puede abrir el acceso de GitHub; no escribir contraseñas ni tokens en el código o en la URL. Si hay cambios remotos, integrarlos conscientemente; no usar `push --force` para resolverlo automáticamente. [Guía oficial de publicación](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

4. Abrir el repositorio, comprobar carpetas e historial y añadir URL del repo y de Wokwi (si procede) al registro de entrega.
5. Continuar con commits reales: `test: registrar mediciones del HC-SR04`, `fix: corregir inversion del motor derecho`, `test: medir parada por timeout`, según lo que efectivamente ocurra. No crear commits vacíos ni cambiar fechas para simular semanas de trabajo.

Ejemplo tras una prueba real:

```powershell
git add evidence/PRUEBAS_FISICAS.md
git commit -m 'test: registrar mediciones reales de distancia y parada'
git push
```

No se publicó un repositorio remoto en esta sesión: falta la URL elegida y el acceso de la cuenta. Los commits locales corresponden a etapas reales de esta preparación, no a evidencia histórica de trabajo anterior.
