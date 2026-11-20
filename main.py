#codigo del main
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
    page.window.min_width = 800
    page.window.min_height = 570
    page.padding = 14
    estado, distancia, potencia = [ft.Text(size=24, weight=ft.FontWeight.BOLD) for _ in range(3)]
    aviso = ft.Text()
    grafica, serie = crear_grafica()
    muestras = []
    tabla = crear_tabla()
    selector = ft.Dropdown(label="Sensor", value="Disponible", width=180,
                           options=[ft.DropdownOption(key=t) for t in ("Disponible", "Sin lectura")])

    def refrescar():
        auto.comprobar()
        aplicada = auto.pwm if auto.estado != "Detenido" else 0
        estado.value = auto.estado
        distancia.value = "Sin lectura" if auto.distancia is None else f"{auto.distancia:g} cm"
        potencia.value = f"{aplicada} %"
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

    def cambiar_distancia(e):
        auto.distancia = round(e.control.value)
        refrescar()

    def guardar_distancia(e):
        auto.registrar(f"Distancia ajustada a {round(e.control.value)} cm")
        refrescar()

    ajuste = ft.Slider(min=2, max=400, divisions=398, value=auto.distancia,
                       label="{value} cm", on_change=cambiar_distancia,
                       on_change_end=guardar_distancia)

    def cambiar_sensor(e):
        disponible = selector.value == "Disponible"
        auto.distancia = round(ajuste.value) if disponible else None
        ajuste.disabled = not disponible
        auto.registrar("Sensor · " + selector.value)
        refrescar()

    selector.on_select = cambiar_sensor

    def panel(titulo, contenido):
        return ft.Container(bgcolor=PANEL, padding=20, border_radius=16,
                            content=ft.Column([ft.Text(titulo, size=17, weight=ft.FontWeight.BOLD),
                                               contenido], spacing=16))

    def indicador(titulo, valor, icono, color):
        return ft.Container(expand=True, bgcolor=PANEL, border_radius=16, padding=16,
            content=ft.Column([ft.Icon(icono, color=color, size=21),
                               ft.Text(titulo, color=TEXTO_SEC, size=13), valor], spacing=6))

    def pagina(titulo, subtitulo, controles):
        return ft.Column([ft.Column([ft.Text(titulo, size=32, weight=ft.FontWeight.BOLD),
                                     ft.Text(subtitulo, color=TEXTO_SEC)], spacing=4),
                          *controles], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)

    indicadores = ft.Row([
        indicador("Movimiento", estado, ft.Icons.DIRECTIONS_CAR, AZUL),
        indicador("Distancia frontal", distancia, ft.Icons.SENSORS, VERDE),
        indicador("PWM aplicado", potencia, ft.Icons.SPEED, AMARILLO)], spacing=12)
    botones = [ft.Button(nombre, on_click=ordenar(nombre)) for nombre in
               ("Avanzar", "Retroceder", "Izquierda", "Derecha")]
    botones.append(ft.Button("Detener", bgcolor=ROJO, on_click=ordenar("Detenido")))
    mando = panel("Control de movimiento", ft.Column([
        ft.Row(botones, wrap=True, spacing=8),
        ft.Text("Potencia seleccionada (%)", color=TEXTO_SEC),
        ft.Slider(min=0, max=100, divisions=100, value=40, label="{value} %", on_change=cambiar_pwm),
        ft.Text("Distancia simulada (cm)", color=TEXTO_SEC), ajuste,
        ft.Row([selector, aviso], wrap=True)], spacing=12))
    tablero = pagina("Panel del vehículo", "ESP32  /  Simulación local", [
        indicadores, mando, panel("Distancia frontal · últimas 10 muestras (cm)", grafica)])
    registros = pagina("Historial", "Últimos 30 eventos de esta sesión", [
        panel("Registro de actividad", tabla)])
    vistas = [tablero, registros]
    area = ft.Container(content=tablero, expand=True, padding=16)

    def cambiar_vista(e):
        area.content = vistas[e.control.selected_index]
        page.update()

    menu = ft.NavigationRail(selected_index=0, extended=True, min_extended_width=172,
        bgcolor=PANEL, on_change=cambiar_vista,
        leading=ft.Container(padding=18, content=ft.Image(src="logo.png", width=126,
                                height=90, fit=ft.BoxFit.CONTAIN)),
        destinations=[ft.NavigationRailDestination(icon=icono, label=texto)
                      for icono, texto in [(ft.Icons.DASHBOARD, "Panel"),
                                           (ft.Icons.TABLE_CHART, "Historial")]])
    page.add(ft.Row([ft.Container(content=menu, bgcolor=PANEL, border_radius=16,
                                  padding=8), area], expand=True, spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH))
    refrescar()
    while page.session:
        if auto.distancia is None:
            muestras.clear()
        else:
            muestras.append(auto.distancia)
            muestras = muestras[-10:]
        serie.points = [LineChartDataPoint(i, d) for i, d in enumerate(muestras)]
        if area.content is tablero:
            grafica.update()
        await asyncio.sleep(1)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ASSETS))
