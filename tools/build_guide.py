"""Reúne las guías editables y crea una versión HTML para leer/imprimir."""
import re
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["docs/01_arquitectura.md", "docs/02_montaje.md", "docs/03_entorno.md",
           "broker/README.md", "docs/04_mqtt.md", "docs/05_pruebas.md",
           "simulation/README.md", "docs/06_rubrica.md", "docs/07_parcial3.md",
           "evidence/VALIDACION.md", "docs/FUENTES.md"]


def main():
    intro = """# Parcial 2 · Vehículo móvil con ESP32 y MQTT

Guía integral de Programación II. Preparada el 29 de octubre de 2026.

**Entrega:** firmware modular, montaje de referencia, entorno de desarrollo,
contrato MQTT, pruebas, simulación preparada y diseño de continuidad al Parcial 3.

**Alcance de validación:** consultar el registro incluido. La verificación en PC
no constituye una prueba física ni una ejecución confirmada en Wokwi.

**Fuentes editables:** las secciones originales están en `docs/`, `broker/`,
`simulation/` y `evidence/`. Este documento se regenera con `tools/build_guide.py`.

"""
    sections = []
    for source in SOURCES:
        body = (ROOT / source).read_text(encoding="utf-8")
        body = body.replace("../diagrams/", "diagrams/")
        sections.append(body)
    markdown = intro + "\n\n---\n\n".join(sections)
    (ROOT / "GUIA_PARCIAL_2.md").write_text(markdown, encoding="utf-8")
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    body = md.render(markdown)
    body = re.sub(r'(<pre><code class="language-mermaid">.*?</code></pre>)',
                  r'<details><summary>Fuente editable del diagrama de flujo</summary>\1</details>', body, flags=re.S)
    css = """
body{margin:0;background:#eef3f8;color:#20334a;font:17px/1.65 'Segoe UI',Arial,sans-serif}
main{max-width:1080px;margin:36px auto;background:white;padding:50px 65px;border-top:9px solid #167d9a;border-radius:8px}
h1{font-size:32px;line-height:1.25;margin:40px 0 20px;color:#123553}h2{font-size:24px;margin-top:36px;color:#16718b}
h3{font-size:20px}a{color:#086e9e}img{max-width:100%;height:auto}pre{background:#f1f5fa;padding:18px;overflow:auto;font-size:14px;line-height:1.5;border-left:4px solid #7fa6c5}
code{font-family:Consolas,monospace}p code,li code{background:#f1f5fa;padding:2px 4px;border-radius:3px}
table{width:100%;border-collapse:collapse;font-size:15px;margin:24px 0}th,td{border:1px solid #cdd9e4;padding:10px 12px;text-align:left;vertical-align:top}
th{background:#e9f3f7}tr:nth-child(even){background:#f9fbfd}hr{margin:60px 0;border:0;border-top:2px solid #b7cad8}details{padding:12px;background:#f7f9fc}summary{cursor:pointer}
@media print{body{background:white;font-size:11pt}main{margin:0;padding:0;border:0;max-width:none}h1{break-before:page;font-size:22pt}main>h1:first-child{break-before:auto}h1,h2,h3{break-after:avoid}tr,img,pre{break-inside:avoid}pre{white-space:pre-wrap;font-size:9pt}a{color:inherit}details{display:none}}
"""
    html = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Parcial 2 · Vehículo MQTT</title><style>' + css + '</style></head><body><main>' + body + '</main></body></html>'
    (ROOT / "GUIA_PARCIAL_2.html").write_text(html, encoding="utf-8")
    print("Guías consolidadas generadas: GUIA_PARCIAL_2.md / .html")


if __name__ == "__main__":
    main()
