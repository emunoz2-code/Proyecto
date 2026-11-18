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

    def bloqueo(self):
        if self.distancia is None:
            return "Sensor sin lectura"
        if self.distancia <= 20:
            return "Obstáculo a 20 cm o menos"
        if self.pwm == 0:
            return "Potencia en cero"
        return ""

    def mover(self, orden):
        motivo = self.bloqueo()
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
