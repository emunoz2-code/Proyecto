import flet as ft
import flet_charts as fch
from estilos import AZUL, PANEL_2


def crear_grafica():
    serie = fch.LineChartData(color=AZUL, stroke_width=3, curved=False, point=True)
    grafica = fch.LineChart(
        height=180, min_x=0, max_x=9, min_y=0, max_y=400, data_series=[serie],
        left_axis=fch.ChartAxis(label_size=40, label_spacing=100),
        bottom_axis=fch.ChartAxis(show_labels=False),
        horizontal_grid_lines=fch.ChartGridLines(interval=100, color=PANEL_2, width=1),
    )
    return grafica, serie


def crear_tabla():
    return ft.DataTable(columns=[ft.DataColumn(label=ft.Text(t)) for t in ("Hora", "Evento")])
