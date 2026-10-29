# Broker Mosquitto para el laboratorio

El firmware usa MQTT 3.1.1 por TCP, puerto 1883, con usuario/contraseña. **No implementa TLS**. Usar red local de laboratorio confiable y sin redirección de puertos desde Internet; las credenciales de 1883 no viajan cifradas. Un broker público se reserva para simulación sin motores físicos ni datos privados.

1. Instalar [Mosquitto para Windows](https://mosquitto.org/download/). Si el instalador crea un servicio, comprobar si ya ocupa el puerto antes de arrancar otra instancia.
2. Desde la raíz del proyecto copiar:

```powershell
Copy-Item '.\broker\mosquitto.example.conf' '.\broker\mosquitto.local.conf'
Copy-Item '.\broker\acl.example' '.\broker\acl.local'
```

3. Para ensayos solo en PC dejar `listener 1883 127.0.0.1`. Para ESP32, usar `ipconfig`, identificar la IPv4 de la interfaz Wi-Fi y sustituir `127.0.0.1` por esa IP, por ejemplo `192.168.1.10`. La ESP32 y la consola deberán conectarse a la misma IP. Si la IP cambia por DHCP, actualizar la configuración o reservarla en el router.
4. Crear dos usuarios, con contraseñas diferentes introducidas interactivamente:

```powershell
& 'C:\Program Files\mosquitto\mosquitto_passwd.exe' -c '.\broker\passwords' carro
& 'C:\Program Files\mosquitto\mosquitto_passwd.exe' '.\broker\passwords' operador
```

La opción `-c` crea/sobrescribe el archivo: usarla solo la primera vez. `passwords` y los archivos locales están excluidos de Git.

5. Ajustar las rutas de topics de `acl.local` si se cambia equipo o vehículo. `carro` puede leer comandos y publicar sus estados; `operador` puede emitir comandos y leer esos estados. Mantener los nombres sincronizados con `config_local.py` y `--base`.
6. Arrancar desde la raíz, pues las rutas del archivo son relativas a ese directorio:

```powershell
& 'C:\Program Files\mosquitto\mosquitto.exe' -c '.\broker\mosquitto.local.conf' -v
```

7. Si Windows solicita acceso de red, limitarlo al perfil privado que corresponda. Si hay que crear una regla manual, restringir puerto 1883 a la subred del laboratorio; no desactivar todo el firewall.
8. Iniciar la consola con el usuario operador y esperar telemetría de la placa.

Pruebas de aceptación: credenciales equivocadas deben fallar; el usuario carro no puede publicar en `cmd`; operador no puede falsificar `telemetry`. La configuración está preparada, pero estas comprobaciones requieren ejecutar Mosquitto y se registran como pendientes hasta realizarlas.

El archivo de ejemplo escucha solo en loopback para evitar abrir innecesariamente la red al copiarlo. La persistencia se desactiva en este laboratorio: reiniciar el broker elimina mensajes retenidos almacenados. Esto no reemplaza las protecciones de sesión del firmware.

Fuentes: [configuración oficial de Mosquitto](https://mosquitto.org/man/mosquitto-conf-5.html), [usuarios con mosquitto_passwd](https://mosquitto.org/man/mosquitto_passwd-1.html).
