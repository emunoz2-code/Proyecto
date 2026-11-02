"""Cliente con la estructura del ejemplo de clase, adaptado al vehiculo.

Conserva conectar/publicar/suscribir/recibirmensaje. El transporte incluido
evita esperar tramas incompletas durante el movimiento y expone RETAIN.
No utiliza umqtt.simple: ver la explicacion en README.md.
"""
import config as cfg
from mqtt_wire import MQTTClient


class ClienteMQTT:
    def __init__(self, id_cliente, broker, topico_base=None):
        self._id_cliente = id_cliente
        self._base = (topico_base or cfg.TOPIC_BASE).rstrip("/")
        self._funcion = None
        self._cliente = MQTTClient(cfg, self._recibir, broker=broker)

    @property
    def listo(self):
        """True cuando el broker confirma la suscripcion de comandos."""
        return self._cliente.ready

    def conectar(self):
        if self._funcion is None:
            raise ValueError("Registrar suscribir(topico, funcion) antes de conectar")
        self._cliente.connect(self._id_cliente, self._base)
        print("Conectado a MQTT; esperando confirmacion de suscripcion")

    def publicar(self, topico, mensaje, retain=False):
        # El transporte acepta texto o bytes y realiza la codificacion.
        self._cliente.publish(topico, mensaje, retain=retain)

    def suscribir(self, topico, funcion):
        """Registrar el receptor; conectar envia SUBSCRIBE y lo repite al reconectar.

        Este vehiculo recibe comandos en un unico topic BASE/cmd. La funcion
        recibe (topico_bytes, mensaje_bytes, retenido_bool).
        """
        if isinstance(topico, bytes):
            topico = topico.decode()
        if topico != self._base + "/cmd":
            raise ValueError("El topic de comandos debe ser BASE/cmd")
        if not callable(funcion):
            raise ValueError("La funcion receptora debe ser invocable")
        self._funcion = funcion

    def _recibir(self, topico, mensaje, retenido):
        if topico == self._base + "/cmd" and self._funcion is not None:
            self._funcion(topico.encode(), mensaje, retenido)

    def recibirmensaje(self):
        self._cliente.poll()

    def cerrar(self):
        self._cliente.close()
