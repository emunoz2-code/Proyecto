from datetime import datetime
from pathlib import Path
import sqlite3
from contextlib import closing


class Vehiculo:
    def __init__(self):
        self.estado = "Detenido"
        self.margen = 8
        self.pwm = 40
        self.distancia = 100
        carpeta = Path.home() / ".atlas-operaciones"
        carpeta.mkdir(exist_ok=True)
        self.archivo = carpeta / "bitacora.sqlite"
        with closing(sqlite3.connect(self.archivo)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS eventos (fecha TEXT, mensaje TEXT)")
            self.eventos = db.execute("SELECT fecha,mensaje FROM eventos ORDER BY rowid DESC LIMIT 200").fetchall()
        self.registrar("Inicio de la simulación")

    def registrar(self, mensaje):
        dato = (datetime.now().isoformat(" ", timespec="seconds"), mensaje)
        with closing(sqlite3.connect(self.archivo)) as db, db:
            db.execute("INSERT INTO eventos VALUES (?,?)", dato)
        self.eventos.insert(0, dato)
        del self.eventos[200:]

    # Escena simplificada: una pared oblicua queda más cerca por la derecha.
    FACTORES = {"Avanzar": -1, "Retroceder": 1, "Derecha": -0.35, "Izquierda": 0.35,
                "Avanzar derecha": -0.95, "Avanzar izquierda": -0.46,
                "Retroceder derecha": 0.46, "Retroceder izquierda": 0.95}

    def simular(self, segundos):
        factor = self.FACTORES.get(self.estado, 0)
        if self.distancia is None or not factor:
            return
        limite = self.margen if factor < 0 else 2
        cambio = factor * 30 * min(self.pwm, getattr(self,'tope',100)) / 100 * segundos
        self.distancia = min(400, max(limite, self.distancia + cambio))
        self.comprobar()

    def bloqueo(self, orden=None):
        if self.distancia is None:
            return "Sensor sin lectura"
        if self.distancia <= self.margen and self.FACTORES.get(orden or self.estado, 0) <= 0:
            return f"Obstáculo a {self.margen} cm o menos"
        if self.pwm == 0:
            return "Potencia en cero"
        return ""

    def mover(self, orden):
        motivo = self.bloqueo(orden)
        if motivo and orden != "Detenido":
            self.estado = "Detenido"
            self.registrar("Orden bloqueada · " + motivo)
        else:
            self.estado = orden
            self.registrar(orden)

    def comprobar(self):
        if self.bloqueo() and self.estado != "Detenido":
            self.estado = "Detenido"
            self.registrar("Parada automática · " + self.bloqueo())
