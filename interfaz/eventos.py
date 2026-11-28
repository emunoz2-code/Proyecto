"""Centro de eventos: consulta, notas de turno y exportaciones de escritorio."""
import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime
import flet as ft

TIPOS = {
    "Alerta": (ft.Icons.WARNING_AMBER, "#FF8C72"),
    "Rescate": (ft.Icons.LOCAL_FIRE_DEPARTMENT, "#FFBC68"),
    "Mando": (ft.Icons.GAMEPAD, "#62DAB3"),
    "Nota": (ft.Icons.EDIT_NOTE, "#C3A3FF"),
    "Sistema": (ft.Icons.INFO_OUTLINE, "#8CBBE7"),
}

def tipo(texto):
    m = texto.casefold()
    if any(t in m for t in ("alerta", "bloquead", "parada automática")): return "Alerta"
    if m.startswith("nota ·"): return "Nota"
    if any(t in m for t in ("bomba","fuego","incendio")): return "Rescate"
    if any(t in m for t in ("avanzar","retroceder","izquierda","derecha","detenido","potencia")): return "Mando"
    return "Sistema"

class Eventos:
    def __init__(self, page, auto):
        self.page, self.auto = page, auto
        self.filtro = "Todos"
        self.limite = 15
        self.firma = None
        self.datos = []
        self.busca = ft.TextField(label="Buscar por mensaje, fecha u hora", prefix_icon=ft.Icons.SEARCH,
                                  on_change=self.filtrar)
        self.total = ft.Text()
        self.lista = ft.Column(spacing=6)
        self.filtros = ft.Row(wrap=True)
        self.mas = ft.TextButton("Mostrar 15 más",on_click=self.ampliar)
        self.seleccion=set()
        self.editando=False
        self.editar=ft.TextButton("Seleccionar",icon=ft.Icons.CHECKLIST,on_click=self.modo_seleccion)
        self.quitar=ft.TextButton("Borrar selección",icon=ft.Icons.DELETE_OUTLINE,on_click=lambda e:self.confirmar_lote(False))
        self.marcar=ft.TextButton("Marcar resultados",on_click=self.marcar_resultados)
        self.vaciar=ft.TextButton("Vaciar historial…",icon=ft.Icons.DELETE_SWEEP,on_click=lambda e:self.confirmar_lote(True))
        self.control = ft.Column([self.busca,self.filtros,self.total,ft.Row([self.editar,self.marcar,self.quitar,self.vaciar],wrap=True),self.lista,self.mas,
            ft.Divider(), ft.Row([ft.Button("Añadir nota",icon=ft.Icons.ADD,on_click=self.nota),
            ft.TextButton("Guardar CSV",icon=ft.Icons.DOWNLOAD,on_click=self.csv),
            ft.TextButton("Guardar JSON",icon=ft.Icons.DOWNLOAD,on_click=self.json)],wrap=True)])
    def filtrar(self,e=None):
        self.limite=15
        self.seleccion.clear()
        self.actualizar()
        self.page.update()
    def ampliar(self,e):
        self.limite+=15
        self.actualizar()
        self.page.update()
    def categoria(self,n):
        def elegir(e):
            self.filtro=n
            self.filtrar()
        return elegir
    def actualizar(self):
        firma=(id(self.auto.eventos), self.auto.eventos[:1],len(self.auto.eventos),self.filtro,self.busca.value,self.limite)
        if firma==self.firma:return
        self.firma=firma
        with closing(sqlite3.connect(self.auto.archivo)) as db, db:
            filas=db.execute("SELECT rowid,fecha,mensaje FROM eventos ORDER BY rowid DESC LIMIT 200").fetchall()
        self.datos=[(i,h,tipo(m),m) for i,h,m in filas if (self.filtro=="Todos" or tipo(m)==self.filtro)
            and (self.busca.value or "").casefold() in (h+" "+m).casefold()]
        self.filtros.controls=[ft.TextButton(f"{n} · {len(filas) if n=='Todos' else sum(tipo(m)==n for _,_,m in filas)}",
            icon=ft.Icons.CHECK if n==self.filtro else None,on_click=self.categoria(n)) for n in ["Todos",*TIPOS]]
        self.total.value=f"{len(self.datos)} coincidencias   /   {len(filas)} eventos recientes"
        self.seleccion.intersection_update(d[0] for d in self.datos)
        self.editar.content="Cancelar selección" if self.editando else "Seleccionar"
        self.marcar.visible=self.quitar.visible=self.editando
        self.vaciar.visible=not self.editando
        self.quitar.disabled=not self.seleccion
        self.quitar.content=f"Borrar selección ({len(self.seleccion)})"
        self.marcar.content="Desmarcar resultados" if self.datos and len(self.seleccion)==len(self.datos) else "Marcar resultados"
        self.lista.controls=[]
        for dato in self.datos[:self.limite]:
            i,h,t,m=dato
            marca=ft.Icon(ft.Icons.CHECK_BOX if i in self.seleccion else ft.Icons.CHECK_BOX_OUTLINE_BLANK) if self.editando else ft.Icon(TIPOS[t][0],color=TIPOS[t][1])
            self.lista.controls.append(ft.ListTile(bgcolor="#25483F" if i in self.seleccion else "#1A3038",
                leading=marca,title=ft.Text(m),subtitle=ft.Text(f"{h}   ·   {t}"),
                trailing=None if self.editando else ft.Icon(ft.Icons.CHEVRON_RIGHT),
                on_click=lambda e,d=dato:self.alternar(d[0]) if self.editando else self.detalle(d)))
        if not self.lista.controls:self.lista.controls=[ft.Text("No hay eventos que coincidan con tu búsqueda.")]
        self.mas.visible=len(self.datos)>self.limite
    def redibujar(self):
        self.firma=None
        self.actualizar()
        self.page.update()
    def modo_seleccion(self,e):
        self.editando=not self.editando
        self.seleccion.clear()
        self.redibujar()
    def alternar(self,i):
        self.seleccion.symmetric_difference_update({i})
        self.redibujar()
    def marcar_resultados(self,e):
        ids={d[0] for d in self.datos}
        self.seleccion=set() if ids==self.seleccion else ids
        self.redibujar()
    def confirmar_lote(self,todo):
        ids=tuple(self.seleccion)
        with closing(sqlite3.connect(self.auto.archivo)) as db:
            mayor,total=db.execute("SELECT MAX(rowid),COUNT(*) FROM eventos").fetchone()
        cantidad=total if todo else len(ids)
        if not cantidad:return
        def eliminar(e):
            with closing(sqlite3.connect(self.auto.archivo)) as db,db:
                if todo: db.execute("DELETE FROM eventos WHERE rowid<=?",(mayor,))
                else: db.executemany("DELETE FROM eventos WHERE rowid=?",[(i,) for i in ids])
                self.auto.eventos=db.execute("SELECT fecha,mensaje FROM eventos ORDER BY rowid DESC LIMIT 200").fetchall()
            self.page.pop_dialog()
            self.editando=False
            self.seleccion.clear()
            self.redibujar()
        alcance="todo el historial, incluidos los registros ocultos por filtros" if todo else "la selección"
        self.dialogo("¿Vaciar el historial?" if todo else "¿Borrar la selección?",
            ft.Text(f"Se eliminarán {cantidad} registros de {alcance}. No se puede deshacer."),
            [ft.Button(f"Borrar {cantidad}",on_click=eliminar)])
    def dialogo(self,titulo,contenido,acciones):
        self.page.show_dialog(ft.AlertDialog(modal=True,title=ft.Text(titulo),content=contenido,
            actions=[ft.TextButton("Cerrar",on_click=lambda e:self.page.pop_dialog()),*acciones]))
    def detalle(self,d):
        i,h,t,m=d
        def confirmar(e):
            self.page.pop_dialog()
            self.dialogo("¿Eliminar este evento?",ft.Text(m),[ft.Button("Eliminar", on_click=borrar)])
        def borrar(e):
            with closing(sqlite3.connect(self.auto.archivo)) as db, db:
                db.execute("DELETE FROM eventos WHERE rowid=?",(i,))
                self.auto.eventos=db.execute("SELECT fecha,mensaje FROM eventos ORDER BY rowid DESC LIMIT 200").fetchall()
            self.firma=None
            self.page.pop_dialog()
            self.filtrar()
        self.dialogo(f"{t}  /  #{i}",ft.Text(f"{h}\n\n{m}",selectable=True),
                     [ft.TextButton("Eliminar…",icon=ft.Icons.DELETE_OUTLINE,on_click=confirmar)])
    def nota(self,e):
        campo=ft.TextField(label="Observación del operador",multiline=True,max_length=240)
        def guardar(e):
            valor=(campo.value or "").strip()
            if not valor:
                campo.error_text="Escribe la observación antes de guardarla.";self.page.update();return
            self.auto.registrar("Nota · "+valor)
            self.page.pop_dialog()
            self.filtro="Nota";self.busca.value="";self.filtrar()
        self.dialogo("Nueva nota de turno",campo,[ft.Button("Guardar nota",on_click=guardar)])
    async def csv(self,e):await self.exportar("csv")
    async def json(self,e):await self.exportar("json")
    async def exportar(self,ext):
        datos=list(self.datos)
        try:
            ruta=await ft.FilePicker().save_file(dialog_title="Guardar eventos filtrados",
                file_name="atlas-eventos-"+datetime.now().strftime("%Y%m%d-%H%M%S")+"."+ext)
            if not ruta:return
            ruta=Path(ruta)
            if ext=="csv":
                with ruta.open("w",newline="",encoding="utf-8-sig") as f:
                    w=csv.writer(f);w.writerow(["ID","Fecha","Categoría","Mensaje"]);w.writerows(datos)
            else:ruta.write_text(json.dumps([dict(zip(("id","fecha","categoria","mensaje"),d)) for d in datos],
                ensure_ascii=False,indent=2),encoding="utf8")
            self.dialogo("Archivo guardado",ft.Text(str(ruta),selectable=True),[])
        except (OSError,RuntimeError) as err:self.dialogo("No se pudo guardar",ft.Text(str(err)),[])
