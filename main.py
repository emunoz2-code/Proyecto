import asyncio
from pathlib import Path
import flet as ft
from flet_charts import LineChartDataPoint
from estilos import FONDO, PANEL, TEXTO_SEC, AZUL, AMARILLO, VERDE, ROJO
from paneles import crear_grafica, crear_tabla
from vehiculo import Vehiculo

ASSETS = Path(__file__).parent / "assets"


async def main(page: ft.Page):
    auto = Vehiculo()
    page.title = "Control del vehículo"
    page.window.icon = str(ASSETS / "app.ico")
    page.window.width, page.window.height = 1050, 820
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = FONDO
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 24
    estado, distancia, potencia = [ft.Text(size=24, weight=ft.FontWeight.BOLD) for _ in range(3)]
    aviso = ft.Text()
    barra = ft.ProgressBar(color=AZUL)
    grafica, serie = crear_grafica()
    muestras = []
    tabla = crear_tabla()
    ajuste = ft.TextField(label="Distancia simulada (2–400 cm)", value="100", width=230)
    selector = ft.Dropdown(label="Sensor", value="Disponible", width=180,
                           options=[ft.DropdownOption(key=t) for t in ("Disponible", "Sin lectura")])
    ultima_distancia = 100

    def refrescar():
        auto.comprobar()
        aplicada = auto.pwm if auto.estado != "Detenido" else 0
        estado.value = auto.estado
        distancia.value = "Sin lectura" if auto.distancia is None else f"{auto.distancia:g} cm"
        potencia.value = f"{aplicada} %"
        barra.value = aplicada / 100
        aviso.value = auto.bloqueo() or "Camino despejado"
        aviso.color = AMARILLO if auto.bloqueo() else VERDE
        tabla.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(h)), ft.DataCell(ft.Text(m))])
                      for h, m in auto.eventos]
        page.update()

    def ordenar(nombre):
        def pulsar(e):
            auto.mover(nombre)
            refrescar()
        return pulsar

    def cambiar_pwm(e):
        auto.pwm = round(e.control.value)
        refrescar()

    def aplicar(e):
        nonlocal ultima_distancia
        try:
            valor = float(ajuste.value.replace(",", "."))
            if not 2 <= valor <= 400:
                raise ValueError
        except ValueError:
            ajuste.error_text = "Ingresa un número entre 2 y 400."
            page.update()
            return
        ajuste.error_text = None
        ultima_distancia = valor
        auto.distancia = valor
        auto.registrar(f"Distancia ajustada a {valor:g} cm")
        refrescar()

    boton_aplicar = ft.Button("Aplicar distancia", on_click=aplicar)

    def cambiar_sensor(e):
        disponible = selector.value == "Disponible"
        auto.distancia = ultima_distancia if disponible else None
        ajuste.disabled = boton_aplicar.disabled = not disponible
        auto.registrar("Sensor · " + selector.value)
        refrescar()

    selector.on_select = cambiar_sensor

    def tarjeta(titulo, contenido):
        return ft.Container(bgcolor=PANEL, padding=16, border_radius=12,
                            content=ft.Column([ft.Text(titulo, color=TEXTO_SEC), contenido]))

    botones = [ft.Button(nombre, on_click=ordenar(nombre)) for nombre in
               ("Avanzar", "Retroceder", "Izquierda", "Derecha")]
    botones.append(ft.Button("Detener", bgcolor=ROJO, on_click=ordenar("Detenido")))
    page.add(
        ft.Row([ft.Image(src="logo.png", width=100, height=64, fit=ft.BoxFit.CONTAIN),
                ft.Column([ft.Text("Control del vehículo", size=29, weight=ft.FontWeight.BOLD),
                           ft.Text("ESP32 · Simulación local", color=TEXTO_SEC)])]),
        ft.Row([tarjeta("Movimiento", estado), tarjeta("Distancia frontal", distancia),
                tarjeta("PWM aplicado", potencia)], wrap=True),
        tarjeta("Control de movimiento", ft.Column([
            ft.Row(botones, wrap=True), ft.Text("Potencia seleccionada (%)"),
            ft.Slider(min=0, max=100, divisions=100, value=40, label="{value} %", on_change=cambiar_pwm),
            barra, aviso])),
        tarjeta("Sensor ultrasónico", ft.Row([selector, ajuste, boton_aplicar], wrap=True)),
        tarjeta("Distancia (cm) · una muestra por segundo", grafica),
        tarjeta("Historial de la sesión", tabla))
    refrescar()
    while page.session:
        if auto.distancia is None:
            muestras.clear()
        else:
            muestras.append(auto.distancia)
            muestras = muestras[-10:]
        serie.points = [LineChartDataPoint(i, d) for i, d in enumerate(muestras)]
        grafica.update()
        await asyncio.sleep(1)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ASSETS))
