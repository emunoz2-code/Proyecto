"""Prepara archivos en dist/wokwi. Nunca copia config_local.py del hardware."""
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / "dist" / "wokwi"
    target.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / "firmware").glob("*.py"):
        if path.name != "config_local.py" and not path.name.endswith(".example.py"):
            shutil.copy2(path, target / path.name)
    config = (ROOT / "simulation" / "config_wokwi.py").read_text(encoding="utf-8")
    root = "prog2/demo-" + uuid.uuid4().hex[:12]
    config = config.replace("prog2/CAMBIAR_POR_ID_UNICO", root)
    (target / "config_local.py").write_text(config, encoding="utf-8")
    shutil.copy2(ROOT / "simulation" / "diagram.json", target / "diagram.json")
    shutil.copy2(ROOT / "simulation" / "README.md", target / "README.md")
    shutil.make_archive(str(ROOT / "dist" / "wokwi_parcial2"), "zip", target)
    print("Paquete preparado:", target)
    print("Base MQTT de esta exportación:", root + "/carro01")
    print("No se ha ejecutado ni publicado la simulación.")


if __name__ == "__main__":
    main()
