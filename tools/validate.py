"""Guarda evidencia reproducible de pruebas y comprobaciones de archivos."""
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [sys.executable, "tools/check_project.py"],
        [sys.executable, "-m", "pip", "check"],
        [sys.executable, "tools/console.py", "--help"],
    ]
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    output = ["VALIDACION PC - America/Bogota: " + now, "No es prueba física ni ejecución Wokwi.\n"]
    failed = False
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        output.extend(["Comando: " + " ".join(command), result.stdout, result.stderr, "Salida: " + str(result.returncode), ""])
        failed = failed or result.returncode != 0
    path = ROOT / "evidence" / "comprobaciones.txt"
    path.write_text("\n".join(output), encoding="utf-8")
    print("Registro guardado:", path)
    if failed:
        raise SystemExit("Una comprobación falló; consultar registro")
    print("Todas las comprobaciones PC finalizaron correctamente.")


if __name__ == "__main__":
    main()
