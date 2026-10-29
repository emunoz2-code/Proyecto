"""Empaqueta exclusivamente archivos versionados y un historial Git portable."""
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    if git("status", "--porcelain").strip():
        raise SystemExit("Guardar los cambios reales en Git antes de empaquetar.")
    target = ROOT / "dist"
    target.mkdir(exist_ok=True)
    bundle = target / "historial.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=ROOT, check=True)
    paths = git("ls-files", "-z").decode("utf-8").split("\0")
    archive = target / "vehiculo_mqtt_parcial2.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
        for name in filter(None, paths):
            if Path(name).name in ("config_local.py", "passwords", ".env"):
                raise SystemExit("Se encontró un archivo privado versionado; revisar antes de publicar.")
            zipped.write(ROOT / name, name)
        zipped.write(bundle, "historial.bundle")
        zipped.writestr("HISTORIAL_GIT.txt", git("log", "--format=%h %ad %s", "--date=iso-strict", "--reverse"))
    print("Proyecto e historial:", archive)


if __name__ == "__main__":
    main()
