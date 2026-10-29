"""Valida sintaxis y consistencia de archivos, sin afirmar validación física."""
import ast
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    for directory in ("firmware", "tools", "tests", "simulation"):
        for path in (ROOT / directory).glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            count += 1
    diagram = ROOT / "simulation" / "diagram.json"
    if diagram.exists():
        data = json.loads(diagram.read_text(encoding="utf-8"))
        ids = [part["id"] for part in data["parts"]]
        assert len(set(ids)) == len(ids), "Identificador Wokwi repetido"
        for start, end, *_ in data["connections"]:
            for endpoint in (start, end):
                assert endpoint.split(":")[0] in ids or endpoint.startswith("$"), endpoint
    for path in (ROOT / "diagrams").glob("*.svg"):
        ET.parse(path)
    for path in (ROOT / ".run").glob("*.xml"):
        ET.parse(path)
    for directory in (ROOT, ROOT / "docs", ROOT / "broker", ROOT / "simulation", ROOT / "evidence"):
        for path in directory.glob("*.md"):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    assert (path.parent / target.split("#")[0]).exists(), (path, target)
    print(f"Sintaxis Python válida: {count} archivos. JSON y referencias Wokwi comprobados.")
    print("SVG, configuración XML de PyCharm y enlaces Markdown locales válidos.")
    print("No comprueba niveles eléctricos, imports de MicroPython ni ejecución de Wokwi.")


if __name__ == "__main__":
    main()
