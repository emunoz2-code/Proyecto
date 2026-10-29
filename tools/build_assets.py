"""Genera esquemas SVG editables y el diagrama de señales de Wokwi."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def start(width, height, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="context-stroke"/></marker></defs>',
            '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#16324f}.title{font-size:28px;font-weight:700}.label{font-size:19px;font-weight:600}.small{font-size:16px}.tiny{font-size:14px}</style>',
            f'<rect width="{width}" height="{height}" fill="#f5f8fc"/>',
            f'<text x="40" y="48" class="title">{escape(title)}</text>']


def text(svg, x, y, content, style="small", color=None):
    fill = f' style="fill:{color}"' if color else ""
    svg.append(f'<text x="{x}" y="{y}" class="{style}"{fill}>{escape(content)}</text>')


def box(svg, x, y, w, h, title, color="#ffffff"):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{color}" stroke="#b9c9da" stroke-width="2"/>')
    text(svg, x + 18, y + 32, title, "label")


def line(svg, points, color="#187b9a", arrow=False, width=3):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{marker}/>')


def save(svg, name):
    svg.append('</svg>')
    (ROOT / "diagrams" / name).write_text("\n".join(svg), encoding="utf-8")


def architecture():
    s = start(1240, 650, "Vehículo MQTT · Arquitectura del sistema")
    text(s, 40, 82, "Parcial 2: firmware y pruebas | Parcial 3: aplicación gráfica")
    for x, title in ((40, "Computador"), (380, "Broker MQTT"), (740, "ESP32")):
        box(s, x, 160, 250, 170, title)
    text(s, 60, 220, "Consola de ensayo (P2)")
    text(s, 60, 254, "Interfaz de escritorio (P3)")
    text(s, 60, 290, "Órdenes + visualización")
    text(s, 400, 220, "Mosquitto en LAN")
    text(s, 400, 254, "Usuarios y permisos")
    text(s, 400, 290, "Distribuye los mensajes")
    text(s, 760, 220, "MicroPython modular")
    text(s, 760, 254, "Control + límites locales")
    text(s, 760, 290, "Arranque desarmado")
    line(s, "290,200 380,200", arrow=True)
    line(s, "630,200 740,200", arrow=True)
    text(s, 300, 183, "cmd", "tiny")
    text(s, 650, 183, "cmd", "tiny")
    line(s, "740,300 630,300", "#7c5bb5", True)
    line(s, "380,300 290,300", "#7c5bb5", True)
    text(s, 310, 355, "telemetry · ack · heartbeat · availability", "small", "#7c5bb5")
    box(s, 40, 440, 330, 155, "Parada física NC", "#fff0ee")
    text(s, 60, 500, "Contacto 1: corta potencia")
    text(s, 60, 532, "Contacto 2: informa emergencia")
    text(s, 60, 564, "Liberar no reanuda la marcha")
    box(s, 470, 440, 240, 155, "HC-SR04", "#eaf5f8")
    text(s, 490, 500, "Distancia frontal")
    text(s, 490, 532, "ECHO con divisor")
    text(s, 490, 564, "Dato inválido → parar")
    box(s, 850, 440, 340, 155, "L298N + dos motores", "#edf4ec")
    text(s, 870, 500, "Dirección + PWM")
    text(s, 870, 532, "Fuente de potencia separada")
    text(s, 870, 564, "Deshabilitar ≠ freno instantáneo")
    line(s, "710,480 780,480 780,330", arrow=True)
    line(s, "930,330 930,440", arrow=True)
    line(s, "205,440 205,390 805,390 805,330", "#c54f3d", True)
    line(s, "370,570 415,570 415,620 1040,620 1040,595", "#c54f3d", True)
    save(s, "arquitectura.svg")


def wiring():
    s = start(1360, 1170, "ESP32 · L298N · HC-SR04 | Conexiones de referencia")
    text(s, 40, 82, "ESP32 clásica WROOM-32 · Números GPIO, no posiciones físicas · Confirmar esquema del módulo real")
    box(s, 40, 125, 250, 350, "ESP32 · salidas 3.3 V", "#eaf5f8")
    box(s, 610, 125, 280, 350, "Módulo L298N", "#edf4ec")
    rows = [(25, "ENA · PWM izquierdo"), (26, "IN1"), (27, "IN2"),
            (14, "ENB · PWM derecho"), (18, "IN3"), (19, "IN4")]
    for i, (pin, target) in enumerate(rows):
        y = 205 + i * 43
        text(s, 65, y + 6, f"GPIO{pin}", "label")
        text(s, 630, y + 6, target)
        line(s, f"290,{y} 610,{y}", "#187b9a" if i in (0, 3) else "#7c5bb5", True)
    text(s, 328, 170, "Retirar jumpers ENA y ENB", "small")
    box(s, 1030, 160, 290, 115, "Motor izquierdo")
    text(s, 1050, 225, "OUT1 / OUT2")
    box(s, 1030, 325, 290, 115, "Motor derecho")
    text(s, 1050, 390, "OUT3 / OUT4")
    line(s, "890,220 1030,220", "#5d803d", True, 4)
    line(s, "890,385 1030,385", "#5d803d", True, 4)
    text(s, 40, 514, "ENA y ENB: 10 kΩ a GND cada uno. IN1–IN4: 10 kΩ a GND recomendados.")
    text(s, 40, 544, "Todos los GND unidos. Los motores se conectan a OUT1–OUT4, nunca a GPIO ni al pin 3V3.")
    box(s, 40, 580, 250, 230, "ESP32 · sensor", "#eaf5f8")
    box(s, 1050, 580, 270, 230, "HC-SR04")
    text(s, 65, 645, "GPIO23 · TRIG", "label")
    text(s, 1070, 645, "TRIG")
    line(s, "290,640 1050,640", "#187b9a", True)
    text(s, 65, 710, "GPIO34 · entrada", "label")
    text(s, 1070, 710, "ECHO · 5 V")
    line(s, "1050,705 920,705", "#cc7934")
    s.append('<rect x="800" y="694" width="120" height="22" fill="white" stroke="#cc7934" stroke-width="3"/>')
    text(s, 812, 684, "R1: 2.2 kΩ")
    line(s, "800,705 600,705 290,705", "#cc7934", True)
    s.append('<circle cx="600" cy="705" r="5" fill="#cc7934"/>')
    text(s, 380, 685, "Nodo ≈ 3.0 V")
    line(s, "600,705 600,730", "#cc7934")
    s.append('<rect x="589" y="730" width="22" height="46" fill="white" stroke="#cc7934" stroke-width="3"/>')
    text(s, 635, 757, "R2: 3.3 kΩ")
    line(s, "600,776 600,795 750,795", "#536477")
    text(s, 765, 801, "GND")
    text(s, 65, 770, "ECHO nunca directo a 5 V")
    text(s, 1070, 760, "VCC: 5 V regulados")
    text(s, 1070, 790, "GND: referencia común")
    box(s, 40, 840, 1280, 280, "Alimentación y emergencia · Dos contactos NC independientes", "#fff7ed")
    text(s, 65, 905, "Banco: ESP32 por USB. Fuente externa 5 V → lógica L298N y HC-SR04; GND común.")
    text(s, 65, 935, "No unir ese positivo 5 V a VIN/5V de ESP32 con USB conectado. Verificar 5V-EN del módulo.")
    text(s, 65, 990, "Fuente motor +")
    line(s, "225,985 290,985", "#c54f3d", True, 4)
    text(s, 305, 990, "Fusible")
    line(s, "385,985 445,985", "#c54f3d", True, 4)
    text(s, 460, 990, "Contacto NC 1")
    line(s, "620,985 700,985", "#c54f3d", True, 4)
    text(s, 715, 990, "Vs del L298N")
    text(s, 940, 990, "Corte físico de potencia", "small", "#c54f3d")
    text(s, 65, 1050, "3.3 V")
    line(s, "120,1045 185,1045", "#187b9a", True)
    text(s, 200, 1050, "10 kΩ")
    line(s, "270,1045 335,1045", "#187b9a", True)
    text(s, 350, 1050, "GPIO33")
    line(s, "440,1045 510,1045", "#187b9a", True)
    text(s, 525, 1050, "Contacto NC 2")
    line(s, "685,1045 755,1045", "#187b9a", True)
    text(s, 770, 1050, "GND")
    text(s, 940, 1050, "Abierto = emergencia")
    text(s, 65, 1092, "No mezclar los circuitos de ambos contactos. Desconectar energía antes de cambiar cables.")
    text(s, 40, 1150, "Esquema funcional editable; consultar docs/02_montaje.md para dimensionamiento, jumpers, condensadores y procedimiento.", "tiny")
    save(s, "conexiones.svg")


def wokwi():
    parts = [
        {"type": "wokwi-esp32-devkit-v1", "id": "esp", "top": 30, "left": 0, "attrs": {}},
        {"type": "wokwi-hc-sr04", "id": "sensor", "top": -130, "left": 300, "attrs": {"distance": "100"}},
        {"type": "wokwi-slide-switch", "id": "emergency", "top": 400, "left": 250, "attrs": {"value": "0"}},
        {"type": "wokwi-logic-analyzer", "id": "logic", "top": 150, "left": 650, "attrs": {}},
        {"type": "wokwi-resistor", "id": "echo_top", "top": -20, "left": 260, "attrs": {"value": "2200"}},
        {"type": "wokwi-resistor", "id": "echo_bottom", "top": 20, "left": 340, "attrs": {"value": "3300"}},
        {"type": "wokwi-resistor", "id": "pullup", "top": 350, "left": 240, "attrs": {"value": "10000"}},
        {"type": "wokwi-text", "id": "notice", "top": 520, "left": 0, "attrs": {"text": "MODELO DE SENALES: LED no representan motores ni corrientes.\nECHO fisico exige divisor. Interruptor: contacto auxiliar de emergencia."}},
    ]
    connections = [
        ["esp:TX0", "$serialMonitor:RX", "", []], ["esp:RX0", "$serialMonitor:TX", "", []],
        ["esp:VIN", "sensor:VCC", "red", []], ["esp:GND.1", "sensor:GND", "black", []],
        ["esp:D23", "sensor:TRIG", "green", []],
        ["sensor:ECHO", "echo_top:1", "orange", []],
        ["echo_top:2", "esp:D34", "orange", []],
        ["echo_top:2", "echo_bottom:1", "orange", []],
        ["echo_bottom:2", "esp:GND.1", "black", []],
        ["esp:D33", "emergency:2", "blue", []],
        ["emergency:1", "esp:GND.1", "black", []],
        ["esp:3V3", "pullup:1", "red", []], ["pullup:2", "esp:D33", "blue", []],
        ["logic:GND", "esp:GND.1", "black", []],
    ]
    for index, (pin, label) in enumerate(((25, "ENA"), (26, "IN1"), (27, "IN2"), (14, "ENB"), (18, "IN3"), (19, "IN4"))):
        y = 70 + index * 55
        parts.extend([
            {"type": "wokwi-led", "id": "led" + str(index), "top": y, "left": 440, "attrs": {"color": "green" if label.startswith("EN") else "blue", "label": label}},
            {"type": "wokwi-resistor", "id": "r" + str(index), "top": y + 20, "left": 320, "attrs": {"value": "1000"}},
        ])
        connections.extend([
            [f"esp:D{pin}", f"r{index}:1", "green", []],
            [f"r{index}:2", f"led{index}:A", "green", []],
            [f"led{index}:C", "esp:GND.1", "black", []],
            [f"esp:D{pin}", f"logic:D{index}", "purple", []],
        ])
    diagram = {"version": 1, "author": "Proyecto Programacion II", "editor": "wokwi", "parts": parts, "connections": connections}
    (ROOT / "simulation" / "diagram.json").write_text(json.dumps(diagram, indent=2), encoding="utf-8")


if __name__ == "__main__":
    (ROOT / "diagrams").mkdir(exist_ok=True)
    architecture()
    wiring()
    wokwi()
    print("Generados arquitectura.svg, conexiones.svg y simulation/diagram.json")
