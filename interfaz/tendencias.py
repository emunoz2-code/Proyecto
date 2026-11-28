"""Tendencias con reloj monotónico; la inspección nunca pausa el vehículo."""
from collections import deque
from time import monotonic
import flet as ft
from flet_charts import LineChartData, LineChartDataPoint
from estilos import AZUL, TEXTO_SEC
from paneles import crear_grafica

class Tendencia:
    def __init__(self,titulo,unidad,maximo,intervalo,curvas):
        self.unidad=unidad
        self.ventana=30
        self.datos=deque()
        self.captura=None
        self.grafica, primera=crear_grafica(maximo,intervalo,curvas[0][1])
        self.series=[primera]
        for nombre,color in curvas[1:]:
            self.series.append(LineChartData(color=color,stroke_width=2,curved=False,point=False))
        self.grafica.data_series=self.series
        self.grafica.bottom_axis.show_labels=True
        self.grafica.bottom_axis.label_size=26
        self.resumen=ft.Text(size=12,color=TEXTO_SEC)
        self.pie=ft.Text(size=12,color=TEXTO_SEC)
        self.boton=ft.TextButton("Congelar",icon=ft.Icons.PAUSE,on_click=self.congelar)
        self.plazos=ft.Row(wrap=True,spacing=0)
        self.control=ft.Column([ft.Text(titulo,size=16,weight=ft.FontWeight.BOLD),
            ft.Row([ft.Text("● "+n,color=c,size=12) for n,c in curvas],wrap=True),
            ft.Container(content=self.grafica,padding=ft.Padding.only(top=14,bottom=10,right=12)),self.pie,self.resumen,ft.Row([self.plazos,self.boton],wrap=True,run_spacing=4)],spacing=10)
        self.pintar()
    def agregar(self,t,*valores):
        self.datos.append((t,valores))
        while self.datos and self.datos[0][0]<t-120:self.datos.popleft()
        if self.captura is None:self.pintar()
    def limpiar(self):
        self.datos.clear();self.captura=None;self.pintar()
    def plazo(self,n):
        def elegir(e):
            self.ventana=n;self.pintar();e.page.update()
        return elegir
    def congelar(self,e):
        self.captura=list(self.datos) if self.captura is None else None
        self.pintar();e.page.update()
    def pintar(self):
        datos=self.datos if self.captura is None else self.captura
        fin=datos[-1][0] if datos else monotonic()
        filas=[(t-fin,vs) for t,vs in datos if t>=fin-self.ventana]
        self.grafica.min_x=-self.ventana;self.grafica.max_x=0
        self.grafica.bottom_axis.label_spacing=self.ventana//3
        for i,serie in enumerate(self.series):
            serie.points=[LineChartDataPoint(t,v[i]) for t,v in filas]
        valores=[v[0] for t,v in filas]
        self.resumen.value=(f"Mín. {min(valores):.1f}   /   Media {sum(valores)/len(valores):.1f}   /   Máx. {max(valores):.1f} {self.unidad}"
                            if valores else "Esperando primera lectura")
        self.pie.value=f"Horizontal: tiempo (s) · 0 = última lectura   |   Vertical: {self.unidad}"
        self.boton.content="Volver al directo" if self.captura is not None else "Congelar"
        self.plazos.controls=[ft.TextButton(f"{n} s",icon=ft.Icons.CHECK if n==self.ventana else None,
                                on_click=self.plazo(n)) for n in (15,30,120)]
