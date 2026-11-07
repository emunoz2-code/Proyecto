from umqtt.simple import MQTTClient

class ClienteMQTT:
    
    def __init__(self, id_cliente, broker):
        self._cliente = MQTTClient(id_cliente, broker)

    def conectar(self):
        self._cliente.connect()
        print("Conectado a MQTT")

    def publicar(self, topico, mensaje):
        self._cliente.publish(topico.encode(), mensaje.encode())

    def suscribir(self, topico, funcion):
        self._cliente.set_callback(funcion)
        self._cliente.subscribe(topico.encode())

    def recibirmensaje(self):
        self._cliente.check_msg()
