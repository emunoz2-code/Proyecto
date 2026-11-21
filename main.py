#codigo del main
import asyncio
from pathlib import Path
from time import monotonic
import flet as ft
from flet_charts import LineChartDataPoint
from estilos import PANEL_2, FONDO, PANEL, TEXTO_SEC, AZUL, AMARILLO, VERDE, ROJO
from paneles import crear_grafica, crear_tabla
from incendio import Incendio
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
        actualizar_rescate()
        aplicada = auto.pwm if auto.estado != "Detenido" else 0
        estado.value = auto.estado
        distancia.value = "Sin lectura" if auto.distancia is None else f"{auto.distancia:.1f} cm"
        potencia.value = f"{aplicada} %"
        aviso.value = auto.bloqueo() or "Camino despejado"
        aviso.color = AMARILLO if auto.bloqueo() else VERDE
        tabla.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(h)), ft.DataCell(ft.Text(m))])
                      for h, m in auto.eventos]
        page.update()

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
    def fila(*controles):
        return ft.Row(list(controles), alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    palanca = ft.Container(width=50, height=50, left=65, top=65,
                           border_radius=25, bgcolor=AZUL)
    ultima_orden = "Detenido"

    def orientar(x, y):
        nonlocal ultima_orden
        radio = (x*x + y*y)**0.5
        escala = min(1, 58 / max(1, radio))
        orden = "Detenido"
        if radio >= 18:
            if min(abs(x), abs(y)) >= 0.4142 * max(abs(x), abs(y)):
                orden = ("Retroceder" if y > 0 else "Avanzar") + (" derecha" if x > 0 else " izquierda")
            elif abs(x) > abs(y):
                orden = "Derecha" if x > 0 else "Izquierda"
            else:
                orden = "Retroceder" if y > 0 else "Avanzar"
        else:
            x = y = 0
        palanca.left, palanca.top = 65 + x*escala, 65 + y*escala
        if orden != ultima_orden:
            auto.mover(orden)
            ultima_orden = orden
        refrescar()

    def arrastrar(e):
        orientar(e.local_position.x - 90, e.local_position.y - 90)

    def soltar(e):
        orientar(0, 0)

    base = ft.Stack([
        ft.Container(width=180, height=180, border_radius=90, bgcolor=FONDO),
        *[ft.Text(t, left=x, top=y, color=TEXTO_SEC) for t,x,y in
          [("▲",84,6), ("▼",84,153), ("◀",8,79), ("▶",155,79)]],
        palanca], width=180, height=180)
    joystick = ft.GestureDetector(content=base, on_pan_start=arrastrar,
        on_pan_update=arrastrar, on_pan_end=soltar, on_pan_cancel=soltar, drag_interval=30)
    anillo = ft.ProgressRing(value=0, width=72, height=72, stroke_width=8, color=AZUL)
    porcentaje = ft.Text()
    mando = panel("Joystick", ft.Column([fila(joystick),
        ft.Text("Arrastra para conducir. Suelta para detener.", color=TEXTO_SEC), fila(anillo, porcentaje)]))
    ajustes = panel("Ajustes de conducción", ft.Column([
        ft.Text("Potencia seleccionada (%)"),
        ft.Slider(min=0, max=100, divisions=100, value=40, label="{value} %", on_change=cambiar_pwm),
        ft.Text("Distancia frontal simulada (cm)"), ajuste, grafica, selector, aviso], spacing=10))
    mando.col = ajustes.col = {"xs":12, "sm":6}
    tablero = pagina("Conducción", "Vehículo ESP32  /  Simulación local", [
        indicadores, ft.ResponsiveRow([mando, ajustes], spacing=14, run_spacing=14)])
    registros = pagina("Historial", "Últimos 30 eventos de esta sesión", [
        panel("Registro de actividad", tabla)])
    fuego = Incendio()
    lectura = ft.Text(size=18)
    alcance = ft.Text()
    bomba = ft.Button("Encender bomba")
    termica, curva = crear_grafica(100, 25, AMARILLO)
    temperaturas = []

    def actualizar_rescate():
        fuego.evaluar()
        alcance.value = f"Distancia al foco: {fuego.distancia} cm · alcance: {fuego.alcance} cm"
        alarma = "Fuego detectado" if fuego.detectado else ("Foco fuera de alcance" if fuego.fuego else "Sin fuego")
        lectura.value = alarma + (" · Bomba encendida" if fuego.bomba else " · Bomba apagada")
        bomba.content = "Apagar bomba" if fuego.bomba else "Encender bomba"
        bomba.disabled = fuego.automatico
        valor = auto.pwm if auto.estado != "Detenido" else 0
        anillo.value = valor / 100
        porcentaje.value = f"PWM de los motores: {valor} %"

    def medir_temperatura():
        temperaturas.append(fuego.temperatura)
        del temperaturas[:-10]
        curva.points = [LineChartDataPoint(i, t) for i, t in enumerate(temperaturas)]

    def iniciar(e):
        fuego.fuego = True
        fuego.temperatura = 85
        medir_temperatura()
        auto.registrar("Inicio de fuego simulado")
        refrescar()

    def mover_foco(e):
        fuego.distancia = round(e.control.value)
        refrescar()

    def modo(e):
        fuego.automatico = e.control.value
        fuego.bomba = False
        auto.registrar("Bomba en modo " + ("automático" if fuego.automatico else "manual"))
        refrescar()

    def bombear(e):
        if not fuego.automatico:
            fuego.bomba = not fuego.bomba
            auto.registrar("Bomba manual " + ("encendida" if fuego.bomba else "apagada"))
            refrescar()

    bomba.on_click = bombear
    escenario = panel("Escenario", ft.Column([ft.Button("Simular fuego", on_click=iniciar), alcance,
        ft.Slider(min=2, max=200, divisions=198, value=50, label="{value} cm", on_change=mover_foco),
        ft.Switch(label="Bomba automática", value=True, on_change=modo), bomba, lectura]))
    termometro = panel("Temperatura del foco (°C)", termica)
    escenario.col = termometro.col = {"xs":12, "sm":6}
    rescate = pagina("Unidad de bomberos", "Prueba local de detección y extinción", [
        ft.ResponsiveRow([escenario, termometro], spacing=14, run_spacing=14)])
    vistas = [tablero, rescate, registros]
    area = ft.Container(content=tablero, expand=True, padding=16)

    def cambiar_vista(e):
        soltar(e)
        area.content = vistas[e.control.selected_index]
        page.update()

    menu = ft.NavigationRail(selected_index=0, extended=True, min_extended_width=172,
        bgcolor=PANEL, on_change=cambiar_vista,
        leading=ft.Container(padding=18, content=ft.Image(src="logo.png", width=126,
                                height=90, fit=ft.BoxFit.CONTAIN)),
        destinations=[ft.NavigationRailDestination(icon=icono, label=texto)
                      for icono, texto in [(ft.Icons.DASHBOARD, "Panel"),
                                           (ft.Icons.LOCAL_FIRE_DEPARTMENT, "Bomberos"),
                                           (ft.Icons.TABLE_CHART, "Historial")]])
    page.add(ft.Row([ft.Container(content=menu, bgcolor=PANEL, border_radius=16,
                                  padding=8), area], expand=True, spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH))
    refrescar()
    anterior = siguiente = monotonic()
    while page.session:
        ahora = monotonic()
        auto.simular(min(ahora - anterior, 0.1))
        anterior = ahora
        if auto.distancia is not None:
            ajuste.value = round(auto.distancia)
        if ahora < siguiente:
            if auto.estado != "Detenido" or estado.value != auto.estado:
                refrescar()
            await asyncio.sleep(0.1)
            continue
        siguiente = ahora + 1
        if auto.distancia is None:
            muestras.clear()
        else:
            muestras.append(auto.distancia)
            muestras = muestras[-10:]
        serie.points = [LineChartDataPoint(i, d) for i, d in enumerate(muestras)]
        if fuego.paso():
            auto.registrar("Fuego extinguido · bomba apagada")
        medir_temperatura()
        refrescar()
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ASSETS))
