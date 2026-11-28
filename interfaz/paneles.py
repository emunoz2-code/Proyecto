import flet as ft
import flet_charts as fch
from estilos import AZUL, PANEL_2


def crear_grafica(maximo=400, intervalo=100, color=AZUL):
    serie = fch.LineChartData(color=color, stroke_width=3, curved=False, point=False)
    grafica = fch.LineChart(
        height=180, min_x=0, max_x=29, min_y=0, max_y=maximo, data_series=[serie],
        left_axis=fch.ChartAxis(label_size=40, label_spacing=intervalo),
        bottom_axis=fch.ChartAxis(show_labels=False),
        horizontal_grid_lines=fch.ChartGridLines(interval=intervalo, color=PANEL_2, width=1),
    )
    return grafica, serie


def crear_tabla():
    return ft.DataTable(columns=[ft.DataColumn(label=ft.Text(t)) for t in ("Hora", "Evento")])
