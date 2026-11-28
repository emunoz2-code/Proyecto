import json
from time import monotonic
from paho.mqtt import client as mqtt

BASE = "emunoz2/atlas/479614304886635521"
BROKER = "broker.emqx.io"
NOMBRES = {"avanzar":"Avanzar", "retroceder":"Retroceder", "izquierda":"Izquierda",
           "derecha":"Derecha", "detener":"Detenido"}

for vertical in ("avanzar","retroceder"):
    for lado in ("derecha","izquierda"):
        nombre = vertical+" "+lado
        NOMBRES[nombre] = nombre.capitalize()

class Enlace:
    def __init__(self):
        self.automatico, self.bomba, self.bloqueo = True, False, True
        self.cliente = None
        self.lectura = None

    def abrir(self):
        self.cerrar()
        c = self.cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        def conectado(client, _, flags, reason, props):
            if not reason.is_failure: client.subscribe(BASE + "/estado")
        def recibir(client, _, msg):
            if msg.retain or client is not self.cliente: return
            try:
                d = json.loads(msg.payload)
                cm, p = d["distancia"], d["potencia"]
                if cm is not None and (type(cm) not in (float,int) or not 2 <= cm <= 400): return
                if type(p) is not int or not 0 <= p <= 100: return
                if not isinstance(d.get("sesion"),str) or not d["sesion"]: return
                if not all(type(d.get(k)) is bool for k in ("bomba","detectado","automatico","paro")): return
                if d.get("temperatura") is not None and type(d["temperatura"]) not in (float,int): return
                self.lectura = (monotonic(), cm, NOMBRES[d["estado"]], p, d)
            except (ValueError, TypeError, KeyError): pass
        c.on_connect, c.on_message = conectado, recibir
        c.on_disconnect = lambda *_: setattr(self, "lectura", None)
        c.connect_async(BROKER, keepalive=10)
        c.loop_start()

    def enviar(self, orden, potencia, margen):
        lectura = self.lectura
        if self.cliente and self.cliente.is_connected() and lectura and monotonic()-lectura[0]<1.5:
            self.cliente.publish(BASE + "/orden", json.dumps(dict(
                orden="detener" if orden=="Detenido" else orden.lower(),
                potencia=potencia, margen=margen, sesion=lectura[4]["sesion"],
                automatico=self.automatico, bomba=self.bomba, bloqueo=self.bloqueo)), retain=False)

    def cerrar(self):
        if self.cliente:
            self.bloqueo, self.bomba = True, False
            self.enviar("Detenido", 0, 20)
            self.cliente.disconnect()
            self.cliente.loop_stop()
        self.cliente = self.lectura = None
