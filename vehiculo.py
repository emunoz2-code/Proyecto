from datetime import datetime


class Vehiculo:
    def __init__(self):
        self.estado = "Detenido"
        self.pwm = 40
        self.distancia = 100
        self.eventos = []
        self.registrar("Inicio de la simulación")

    def registrar(self, mensaje):
        self.eventos.insert(0, (datetime.now().strftime("%H:%M:%S"), mensaje))
        del self.eventos[30:]

    # Escena simplificada: una pared oblicua queda más cerca por la derecha.
    FACTORES = {"Avanzar": -1, "Retroceder": 1, "Derecha": -0.35, "Izquierda": 0.35,
                "Avanzar derecha": -0.95, "Avanzar izquierda": -0.46,
                "Retroceder derecha": 0.46, "Retroceder izquierda": 0.95}

    def simular(self, segundos):
        factor = self.FACTORES.get(self.estado, 0)
        if self.distancia is None or not factor:
            return
        limite = 20 if factor < 0 else 2
        cambio = factor * 30 * self.pwm / 100 * segundos
        self.distancia = min(400, max(limite, self.distancia + cambio))
        self.comprobar()

    def bloqueo(self, orden=None):
        if self.distancia is None:
            return "Sensor sin lectura"
        if self.distancia <= 20 and self.FACTORES.get(orden or self.estado, 0) <= 0:
            return "Obstáculo a 20 cm o menos"
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
