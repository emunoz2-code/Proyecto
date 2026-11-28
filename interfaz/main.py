import asyncio
from tendencias import Tendencia
from eventos import Eventos
from datetime import datetime
from enlace import Enlace
import flet_charts as fch
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
    page.title = "ATLAS · Estación de operaciones"
    red = Enlace()
    potencia_real = 0
    ultima_bomba_confirmada = None
    orden_remota = "Detenido"
    emergencia = False
    ultima_alerta = ""
    def chip(texto):
        return ft.Container(content=texto, bgcolor=PANEL_2, border_radius=18, padding=8)
    fuente, conexion, reloj = (ft.Text(size=12) for _ in range(3))
    alarma = ft.Text(weight=ft.FontWeight.BOLD)
    cabecera = ft.Row([ft.Image(src="logo.png",width=38,height=38),chip(ft.Text("ATLAS   /   U–01", color=AZUL, weight=ft.FontWeight.BOLD)),
                        chip(fuente), chip(conexion), reloj], wrap=True)
    sonido = ft.Switch(label="Aviso sonoro", value=True)
    buscar = ft.TextField(label="Buscar en los eventos", on_change=lambda e: refrescar())
    resultado = ft.Text(color=AZUL)
    remoto = ft.Switch(label="Usar vehículo Wokwi", value=False)
    limitado = ft.Switch(label="Limitar potencia al 60 %", value=True)
    def limite():
        return min(auto.pwm, 60 if limitado.value else 100)
    def vigente():
        return red.lectura is not None and monotonic()-red.lectura[0]<1.5
    def paro(e):
        nonlocal emergencia, orden_remota
        emergencia = not emergencia
        orden_remota = "Detenido"
        red.bloqueo = emergencia
        red.bomba = False
        red.enviar("Detenido",0,auto.margen)
        auto.mover("Detenido")
        auto.registrar("Bloqueo del mando" if emergencia else "Mando habilitado")
        freno.content = "Rearmar mando" if emergencia else "Bloquear mando"
        refrescar()
    freno = ft.Button("Bloquear mando", on_click=paro, color=ROJO)
    page.window.icon = str(ASSETS / "app.ico")
    page.window.width, page.window.height = 1280, 860
    page.theme = ft.Theme(color_scheme_seed=AZUL)
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = FONDO
    page.window.min_width = 320
    page.window.min_height = 570
    page.padding = 14
    estado, distancia, potencia = [ft.Text(size=24, weight=ft.FontWeight.BOLD) for _ in range(3)]
    aviso = ft.Text()
    proximidad = Tendencia("Proximidad frontal","cm",400,100,[("Distancia al obstáculo",AZUL),("Umbral de parada",AMARILLO)])
    traccion = Tendencia("Respuesta del mando","%",100,25,[("Entregada",AZUL),("Solicitada","#B698FA")])
    eventos = Eventos(page,auto)
    instrucciones = {"Distancia de parada alcanzada":"Suelta el mando y retrocede para ganar espacio.",
        "Sensor sin lectura":"Activa el sensor en Conducción para recuperar la lectura.",
        "Mando bloqueado":"Usa Rearmar mando cuando puedas continuar.",
        "Fuego detectado en simulación":"Abre Rescate para revisar la bomba y la curva de temperatura."}
    def silenciar(e):
        sonido.value = not sonido.value
        refrescar()
    silencio = ft.TextButton(icon=ft.Icons.VOLUME_OFF,on_click=silenciar)
    banda = ft.Container(padding=12,border_radius=12,content=ft.Row([alarma,silencio,freno],wrap=True))
    popups = ft.Switch(label="Abrir aviso al detectar una incidencia",value=True)
    def advertir(motivo):
        if auto.estado != "Detenido":
            auto.mover("Detenido")
        page.show_dialog(ft.AlertDialog(modal=True,icon=ft.Icon(ft.Icons.WARNING_AMBER,color=AMARILLO),
            title=ft.Text(motivo),content=ft.Text(instrucciones.get(motivo,"Comprueba el estado de la unidad.")),
            actions=[ft.TextButton("Ver eventos",on_click=abrir_eventos),
                     ft.Button("Entendido",on_click=lambda e:page.pop_dialog())]))
    def abrir_eventos(e):
        page.pop_dialog()
        navegar(2)
    selector = ft.Switch(label="Sensor disponible", value=True)
    def refrescar():
        nonlocal ultima_alerta
        if not remoto.value:
            auto.comprobar()
        actualizar_rescate()
        aplicada = potencia_real if remoto.value else (limite() if auto.estado != "Detenido" else 0)
        seleccion.value = f"Solicitada: {auto.pwm} %   ·   Límite: {60 if limitado.value else 100} %"
        estado.value = auto.estado
        distancia.value = "Sin lectura" if auto.distancia is None else f"{auto.distancia:.1f} cm"
        potencia.value = "—" if remoto.value and not vigente() else f"{aplicada} %"
        anillo.value = aplicada / 100
        porcentaje.value = f"Potencia aplicada: {aplicada} %"
        fuente.value = "WOKWI  /  MQTT" if remoto.value else "SIMULACIÓN LOCAL"
        conexion.value = ("ESP32 en línea" if vigente() else "Esperando telemetría") if remoto.value else "Laboratorio de maniobras"
        reloj.value = datetime.now().strftime("%H:%M:%S")
        motivo = ("Mando bloqueado" if emergencia else
                  "Sin señal reciente de la ESP32" if remoto.value and not vigente() else
                  "Paro físico activo" if remoto.value and vigente() and red.lectura[4]["paro"] else
                  "Sensor sin lectura" if auto.distancia is None else
                  "Distancia de parada alcanzada" if auto.distancia <= auto.margen else
                  "Foco térmico en Wokwi" if remoto.value and vigente() and red.lectura[4]["detectado"] else
                  "Fuego detectado en simulación" if fuego.detectado and not remoto.value else "")
        alarma.value = "▲   " + motivo if motivo else "●   Operación normal"
        alarma.color = AMARILLO if motivo else VERDE
        banda.bgcolor = "#492C33" if motivo else "#14382F"
        silencio.content = "Silenciar avisos" if sonido.value else "Activar sonido"
        if motivo and motivo != ultima_alerta:
            if popups.value: advertir(motivo)
            auto.registrar("Alerta · " + motivo)
            if sonido.value:
                try:
                    import winsound
                    winsound.MessageBeep()
                except (ImportError, RuntimeError): pass
        ultima_alerta = motivo
        aviso.value = f"Parada configurada a {auto.margen} cm"
        margen_libre = None if auto.distancia is None else auto.distancia-auto.margen
        diagnostico.value = ("Sin lectura de proximidad" if margen_libre is None else
            f"Margen antes de la parada: {margen_libre:.1f} cm" if margen_libre>=0 else
            f"Dentro de la zona de parada por {-margen_libre:.1f} cm")
        guia.value = ("Sensor sin lectura" if margen_libre is None else "Zona de parada" if margen_libre<=0 else
                      "Cerca del límite" if margen_libre<20 else "Espacio disponible")
        guia.color = AMARILLO if margen_libre is None or margen_libre<20 else VERDE
        reserva.color = guia.color
        reserva.value = 0 if margen_libre is None else max(0,min(1,margen_libre/100))
        detalle_reserva.value = diagnostico.value + (" · escala de 100 cm" if margen_libre is not None else "")
        entrega.value = f"Potencia solicitada: {auto.pwm} %   ·   Aplicada: {aplicada} %"
        eventos.actualizar()
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
        disponible = selector.value
        auto.distancia = round(ajuste.value) if disponible else None
        ajuste.disabled = not disponible
        auto.registrar("Sensor disponible" if disponible else "Sensor sin lectura")
        refrescar()

    selector.on_change = cambiar_sensor

    tarjetas = []
    def panel(titulo, contenido):
        tarjeta = ft.Container(bgcolor=PANEL, padding=20, border=ft.Border.all(1,PANEL_2), border_radius=14,
                            content=ft.Column([ft.Text(titulo, size=17, weight=ft.FontWeight.BOLD),
                                               contenido], spacing=16))
        tarjetas.append(tarjeta)
        return tarjeta

    def indicador(titulo, valor, icono, color):
        return ft.Container(col={"xs":6,"sm":4}, bgcolor=PANEL, border_radius=16, padding=16,
            content=ft.Column([ft.Icon(icono, color=color, size=21),
                               ft.Text(titulo, color=TEXTO_SEC, size=13), valor], spacing=6))

    def pagina(titulo, subtitulo, controles):
        return ft.Column([ft.Column([ft.Text(titulo, size=32, weight=ft.FontWeight.BOLD),
                                     ft.Text(subtitulo, color=TEXTO_SEC)], spacing=4),
                          *controles], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)

    indicadores = ft.ResponsiveRow([
        indicador("Movimiento", estado, ft.Icons.DIRECTIONS_CAR, AZUL),
        indicador("Distancia frontal", distancia, ft.Icons.SENSORS, VERDE),
        indicador("Potencia aplicada", potencia, ft.Icons.SPEED, AMARILLO)], spacing=12)
    def fila(*controles):
        return ft.Row(list(controles), alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    palanca = ft.Container(width=50, height=50, left=65, top=65,
                           border_radius=25, bgcolor=AZUL)
    ultima_orden = "Detenido"

    def orientar(x, y):
        nonlocal ultima_orden, orden_remota
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
        if emergencia: orden = "Detenido"
        if remoto.value:
            orden_remota = orden if vigente() and not emergencia else "Detenido"
            red.enviar(orden_remota, limite(), auto.margen)
            ultima_orden = orden_remota
        elif orden != ultima_orden:
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
    anillo = ft.ProgressRing(value=0, width=36, height=36, stroke_width=5, color=AZUL)
    porcentaje = ft.Text()
    mando = panel("Joystick", ft.Column([fila(joystick),
        ft.Text("Arrastra para conducir · suelta para detener · Esc para centrar", color=TEXTO_SEC), fila(anillo, porcentaje)]))
    diagnostico = ft.Text(selectable=True)
    seleccion = ft.Text("Potencia solicitada · 40 %")
    regulador = ft.Slider(min=0,max=100,divisions=100,value=40,label="{value} %",on_change=cambiar_pwm)
    def graduar(delta):
        def ajustar_potencia(e):
            auto.pwm = max(0,min(100,auto.pwm+delta))
            regulador.value = auto.pwm
            refrescar()
        return ajustar_potencia
    fino = ft.Row([ft.IconButton(icon=ft.Icons.REMOVE,tooltip="Bajar cinco puntos",on_click=graduar(-5)),
                   ft.Text("Ajuste fino · 5 %"),
                   ft.IconButton(icon=ft.Icons.ADD,tooltip="Subir cinco puntos",on_click=graduar(5))])
    ajustes = panel("Ajustes de conducción", ft.Column([
        seleccion, regulador, fino,
        ft.Text("Distancia frontal simulada (cm)"), ajuste, aviso, ft.ExpansionTile(leading=ft.Icon(ft.Icons.SENSORS),title=ft.Text("Diagnóstico de proximidad"), controls=[diagnostico,selector])], spacing=10))
    guia = ft.Text(size=22,weight=ft.FontWeight.BOLD)
    reserva = ft.ProgressBar(value=0,color=AZUL,bgcolor=PANEL_2)
    detalle_reserva = ft.Text(color=TEXTO_SEC)
    entrega = ft.Text()
    situacion = panel("Lectura de la maniobra",ft.Column([
        ft.Text("PROXIMIDAD FRONTAL",size=12,color=TEXTO_SEC),
        guia,reserva,detalle_reserva,ft.Divider(),entrega,
        ft.TextButton("Ajustar conducción",icon=ft.Icons.SETTINGS,on_click=lambda e:navegar(3))],spacing=12))
    motor_chart = ft.Container(content=traccion.control,bgcolor=PANEL,border_radius=14,border=ft.Border.all(1,PANEL_2))
    sensor_chart = ft.Container(content=proximidad.control,bgcolor=PANEL,border_radius=14,border=ft.Border.all(1,PANEL_2))
    tarjetas.extend([motor_chart,sensor_chart])
    for tarjeta in (mando,situacion,motor_chart,sensor_chart):
        tarjeta.col = {"xs":12, "md":6}
    tablero = pagina("Puesto de conducción", "UNIDAD 01   /   Tracción y proximidad", [
        indicadores, ft.ResponsiveRow([mando, situacion], spacing=16, run_spacing=12),
        ft.Text("Telemetría en directo",size=20,weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([motor_chart,sensor_chart],spacing=16,run_spacing=12)])
    registros = pagina("Centro de eventos","Registro de la unidad · selecciona una entrada para inspeccionarla",[
        panel("Explorador de actividad",eventos.control)])
    fuego = Incendio()
    lectura = ft.Text(size=18)
    alcance = ft.Text()
    bomba = ft.Button("Encender bomba")
    termica = Tendencia("Respuesta térmica","°C",100,25,[("Temperatura del foco",AMARILLO)])
    def actualizar_rescate():
        if remoto.value:
            dato = red.lectura[4] if vigente() else None
            alcance.value = "Detección: temperatura ≥ 55 °C y objeto frontal a ≤ 80 cm"
            if dato:
                temp = dato["temperatura"]
                lectura.value = ("Sin temperatura" if temp is None else f"{temp:.1f} °C") + (
                    " · Foco detectado" if dato["detectado"] else " · Sin foco confirmado") + (
                    " · Bomba encendida" if dato["bomba"] else " · Bomba apagada") + (
                    " · Automático" if dato["automatico"] else " · Manual")
            else: lectura.value = "Esperando datos de la ESP32"
            bomba.disabled = not dato or red.automatico or emergencia or dato["paro"]
            bomba.content = "Apagar bomba" if red.bomba else "Encender bomba"
            return
        fuego.evaluar()
        alcance.value = f"Distancia al foco: {fuego.distancia} cm · alcance: {fuego.alcance} cm"
        alarma = "Fuego detectado" if fuego.detectado else ("Foco fuera de alcance" if fuego.fuego else "Sin fuego")
        lectura.value = alarma + (" · Bomba encendida" if fuego.bomba else " · Bomba apagada")
        bomba.content = "Apagar bomba" if fuego.bomba else "Encender bomba"
        bomba.disabled = fuego.automatico
        valor = auto.pwm if auto.estado != "Detenido" else 0
        anillo.value = valor / 100
        porcentaje.value = f"Potencia de los motores: {valor} %"

    def medir_temperatura():
        termica.agregar(monotonic(),fuego.temperatura)

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
        red.automatico = e.control.value
        red.bomba = False
        fuego.automatico = e.control.value
        fuego.bomba = False
        auto.registrar("Bomba en modo " + ("automático" if fuego.automatico else "manual"))
        refrescar()

    def bombear(e):
        if remoto.value:
            if vigente() and not red.automatico and not emergencia:
                red.bomba = not red.bomba
                auto.registrar("Solicitud de bomba: " + ("encender" if red.bomba else "apagar"))
                refrescar()
            return
        if not fuego.automatico:
            fuego.bomba = not fuego.bomba
            auto.registrar("Bomba manual " + ("encendida" if fuego.bomba else "apagada"))
            refrescar()

    bomba.on_click = bombear
    generar = ft.Button("Simular fuego", on_click=iniciar)
    distancia_foco = ft.Slider(min=2,max=200,divisions=198,value=50,label="{value} cm",on_change=mover_foco)
    escenario = panel("Escenario", ft.Column([generar, alcance,
        distancia_foco,
        ft.Switch(label="Bomba automática", value=True, on_change=modo), bomba, lectura]))
    termometro = panel("Monitor de extinción", termica.control)
    escenario.col = termometro.col = {"xs":12, "md":6}
    rescate = pagina("Unidad de bomberos", "Prueba local de detección y extinción", [
        ft.ResponsiveRow([escenario, termometro], spacing=14, run_spacing=14)])
    def cambiar_fuente(e):
        nonlocal orden_remota, potencia_real, ultima_orden
        red.cerrar()
        auto.estado = orden_remota = ultima_orden = "Detenido"
        potencia_real = 0
        proximidad.limpiar();traccion.limpiar();termica.limpiar()
        auto.distancia = None if remoto.value else round(ajuste.value)
        selector.disabled = ajuste.disabled = remoto.value
        selector.value = True
        generar.visible = distancia_foco.visible = not remoto.value
        red.bomba = False
        red.automatico = fuego.automatico
        fuego.fuego = fuego.bomba = False
        if remoto.value: red.abrir()
        auto.registrar("Fuente: Wokwi" if remoto.value else "Fuente: simulación")
        refrescar()
    remoto.on_change = cambiar_fuente
    def margen(e):
        auto.margen = round(e.control.value)
        etiqueta.value = f"Distancia de parada: {auto.margen} cm"
        refrescar()
    etiqueta = ft.Text("Distancia de parada: 8 cm")
    limitado.on_change = lambda e: refrescar()
    config = pagina("Parámetros", "Ajustes de la unidad · sesión actual", [ajustes,
        panel("Origen de las lecturas",ft.Column([remoto,ft.Text("Wokwi: cambia la temperatura del NTC y la distancia del HC-SR04 en el montaje.") ])),
        panel("Puesto del operador",ft.Column([popups,sonido,
            ft.ExpansionTile(title=ft.Text("Cómo se interpretan los avisos"),leading=ft.Icon(ft.Icons.INFO_OUTLINE),
            controls=[ft.Text("Cerrar el aviso no elimina su causa. La franja superior indica si la incidencia sigue activa y la bitácora conserva la hora.")])])),
        panel("Límites de operación", ft.Column([limitado,etiqueta,
            ft.Slider(min=2,max=100,divisions=98,value=8,label="{value} cm",on_change=margen),ft.Text("El umbral de simulación admite de 2 a 100 cm.")]))])
    vistas = [tablero, rescate, registros, config]
    area = ft.Container(content=tablero, expand=True, padding=16)

    def cambiar_vista(e):
        navegar(e.control.selected_index)

    menu = ft.NavigationRail(selected_index=0, extended=True, min_extended_width=155,
        bgcolor=PANEL, on_change=cambiar_vista,
        leading=ft.Container(padding=18, content=ft.Image(src="logo.png", width=76,
                                height=90, fit=ft.BoxFit.CONTAIN)),
        destinations=[ft.NavigationRailDestination(icon=icono, label=texto)
                      for icono, texto in [(ft.Icons.DASHBOARD, "Panel"),
                                           (ft.Icons.LOCAL_FIRE_DEPARTMENT, "Bomberos"),
                                           (ft.Icons.NOTIFICATIONS, "Eventos"), (ft.Icons.SETTINGS, "Parámetros")]])
    cuerpo = ft.Row([ft.Container(content=menu, bgcolor=PANEL, border_radius=16,
                                  padding=8), area], expand=True, spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH)
    destinos = [(ft.Icons.GAMEPAD,"Mando"),(ft.Icons.LOCAL_FIRE_DEPARTMENT,"Rescate"),
                (ft.Icons.NOTIFICATIONS,"Eventos"),(ft.Icons.SETTINGS,"Ajustes")]
    movil = ft.NavigationBar(destinations=[ft.NavigationBarDestination(icon=i,label=n) for i,n in destinos],
        selected_index=0, on_change=cambiar_vista,bgcolor=PANEL,height=64)
    def ajustar(e=None):
        ancho = page.width or 1280
        compacto = ancho < 720
        menu.extended = ancho >= 1100
        cuerpo.controls[0].visible = not compacto
        movil.visible = compacto
        page.padding = 0
        marco.padding = ft.Padding.symmetric(horizontal=12 if compacto else 20,vertical=6 if compacto else 14)
        area.padding = ft.Padding.symmetric(horizontal=0 if compacto else 8)
        marco.content.spacing = 8 if compacto else 14
        for tarjeta in tarjetas: tarjeta.padding = 14 if compacto else 20
        for vista in vistas: vista.spacing = 12 if compacto else 20
        for tendencia_ui in (traccion,proximidad,termica):
            tendencia_ui.grafica.height = 168 if compacto else 208
        cabecera.spacing = 6 if compacto else 10
        cabecera.run_spacing = 4
        page.update()
    def navegar(i):
        soltar(None)
        area.content = vistas[i]
        movil.selected_index = menu.selected_index = i
        page.update()
    def teclado(e):
        if e.key in ("Escape","Esc") and area.content is tablero:
            soltar(None)
    page.on_keyboard_event = teclado
    page.on_resize = ajustar
    page.on_disconnect = lambda e: red.cerrar()
    marco = ft.Container(content=ft.Column([cabecera,banda,cuerpo],expand=True),expand=True)
    page.add(ft.SafeArea(content=ft.Column([marco,movil],spacing=0,expand=True),expand=True))
    ajustar()
    refrescar()
    anterior = siguiente = monotonic()
    while page.session:
        ahora = monotonic()
        if remoto.value:
            if vigente():
                _,auto.distancia,auto.estado,potencia_real,dato = red.lectura
                if ultima_bomba_confirmada != dato["bomba"]:
                    auto.registrar("ESP32 · bomba " + ("encendida" if dato["bomba"] else "apagada"))
                    ultima_bomba_confirmada = dato["bomba"]
                red.bloqueo = emergencia
                if dato["paro"]:
                    orden_remota, red.bomba = "Detenido", False
                red.enviar(orden_remota, limite(), auto.margen)
            else:
                ultima_bomba_confirmada = None
                red.bomba = False
                orden_remota,auto.estado,auto.distancia,potencia_real = "Detenido","Sin señal",None,0
        else:
            auto.tope = 60 if limitado.value else 100
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
        if remoto.value and not vigente():
            traccion.limpiar()
        else:
            aplicada = potencia_real if remoto.value else limite() if auto.estado != "Detenido" else 0
            traccion.agregar(ahora,aplicada,auto.pwm)
        if auto.distancia is None:
            proximidad.limpiar()
        else:
            proximidad.agregar(ahora,auto.distancia,auto.margen)
        if not remoto.value and fuego.paso():
            auto.registrar("Fuego extinguido · bomba apagada")
        if not remoto.value: medir_temperatura()
        elif vigente() and red.lectura[4]["temperatura"] is not None:
            termica.agregar(ahora,red.lectura[4]["temperatura"])
        else: termica.limpiar()
        refrescar()
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ASSETS))
