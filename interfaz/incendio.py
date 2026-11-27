class Incendio:
    """Escena local: un foco de fuego y una bomba de agua."""
    alcance = 80

    def __init__(self):
        self.fuego = False
        self.distancia = 50
        self.temperatura = 25
        self.automatico = True
        self.bomba = False

    @property
    def detectado(self):
        return self.fuego and self.distancia <= self.alcance

    def evaluar(self):
        if self.automatico:
            self.bomba = self.detectado

    def paso(self):
        self.evaluar()
        if self.detectado and self.bomba:
            self.temperatura = max(25, self.temperatura - 10)
            if self.temperatura == 25:
                self.fuego = self.bomba = False
                return True
        return False
