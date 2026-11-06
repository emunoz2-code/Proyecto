# Git y GitHub para esta entrega

**Git** guarda versiones del proyecto en el computador. **GitHub** aloja una copia remota para consultarla desde Internet y compartirla con el docente. La carpeta de este proyecto ya tiene Git iniciado, una rama `main` y un historial de commits. No hay que volver a ejecutar `git init` ni borrar `.git`.

## Primera publicación

1. Iniciar sesión en la cuenta propia de GitHub.
2. Crear un repositorio, por ejemplo `vehiculo-esp32-parcial2`. Para que el docente pueda verlo sin invitación, elegir público; si se elige privado, habrá que darle acceso. No activar la creación de README, licencia o `.gitignore`: estos archivos ya se administran localmente.
3. Copiar la URL HTTPS que GitHub muestra para ese repositorio vacío.
4. Desde la carpeta raíz de este proyecto, conectar y subir:

```powershell
git remote -v
git remote add origin URL_HTTPS_DEL_REPOSITORIO
git push -u origin main
```

Sustituir `URL_HTTPS_DEL_REPOSITORIO` por la dirección real copiada de GitHub. El primer comando permite revisar que no exista ya un remoto llamado `origin`; si existe, comprobar su dirección antes de cambiarla. No usar `--force` para resolver un rechazo.

Git puede abrir el inicio de sesión mediante Git Credential Manager. Completar esa autorización en la ventana oficial de GitHub. No escribir contraseñas o tokens en los archivos del proyecto, mensajes de commit o direcciones del remoto.

5. Abrir el repositorio en GitHub y comprobar que se ven el README, la carpeta `correccion_pulsadores` y los commits anteriores. Entrar al enlace de Wokwi desde el README y ejecutar la simulación.

La publicación solo se considera realizada después de que `git push` termine correctamente y se confirme que la rama remota contiene el mismo commit que la local.

## Guardar cambios posteriores

Después de modificar y comprobar algo real del proyecto, desde su carpeta raíz:

```powershell
git status
git diff
git add correccion_pulsadores
git commit -m "fix: describir la correccion realmente realizada"
git push
```

Reemplazar el mensaje de ejemplo por una descripción concreta. Si también se modificó el README principal, añadirlo expresamente con `git add README.md`. `git add` prepara archivos, `git commit` guarda una versión local y `git push` la envía a GitHub. No es necesario crear commits si no hubo cambios.

Las carpetas `.venv`, `output`, `tmp` y `dist`, además de configuraciones privadas indicadas en `.gitignore`, no forman parte de la entrega. Revisar siempre `git status` antes de subir archivos.

## Explicación breve para la sustentación

«Usé Git para guardar versiones del proyecto y poder ver qué cambió en cada etapa. GitHub guarda la copia remota que puede revisar el profesor. El README explica cómo funciona y contiene el enlace a Wokwi. El programa está dividido en un módulo principal, uno para las señales de los motores y otro para el sensor. Cuando hago una modificación, primero la reviso, después la guardo con un commit y finalmente la subo con push».
