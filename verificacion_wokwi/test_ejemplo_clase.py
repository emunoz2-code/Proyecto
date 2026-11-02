"""Integracion del adaptador ClienteMQTT y la funcion red.conectar."""
import importlib.util
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "parcial2_wokwi"))
import config
from cliente_mqtt import ClienteMQTT
from control import Controller
from mqtt_wire import field, packet, take_packet
from test_mqtt import SocketDouble
from test_control import FakeMotors


class EjemploMQTTTests(unittest.TestCase):
    def test_conexion_comando_retenido_movimiento_y_publicacion(self):
        motor = FakeMotors()
        control = Controller(motor, config, lambda: "sesion-prueba")
        control.link(True)
        control.sensor(100, 0)
        recibidos = []

        def recibir(topico, mensaje, retenido):
            recibidos.append((topico, mensaje, retenido))
            control.command(mensaje, retenido, 0)

        cliente = ClienteMQTT("vehiculo-prueba", "broker-del-argumento", "prueba/auto")
        cliente.suscribir("prueba/auto/cmd", recibir)
        sock = SocketDouble([b"\x20\x02\x00\x00", packet(0x90, b"\x00\x01\x00")])
        direccion = [(None, None, None, None, ("127.0.0.1", 1883))]
        with patch("mqtt_wire.socket.getaddrinfo", return_value=direccion) as resolver:
            with patch("mqtt_wire.socket.socket", return_value=sock):
                with patch("builtins.print"):
                    cliente.conectar()
        self.assertEqual(resolver.call_args.args[0], "broker-del-argumento")
        self.assertFalse(cliente.listo)
        cliente.recibirmensaje()
        self.assertTrue(cliente.listo)

        arm = json.dumps({"v": 1, "action": "arm", "session": control.session, "seq": 0}).encode()
        body = field("prueba/auto/cmd") + arm
        sock.chunks.append(packet(0x31, body))
        cliente.recibirmensaje()
        self.assertEqual(recibidos[-1], (b"prueba/auto/cmd", arm, True))
        self.assertFalse(control.armed)
        sock.chunks.append(packet(0x30, body))
        cliente.recibirmensaje()
        self.assertTrue(control.armed)

        move = json.dumps({"v": 1, "action": "move", "session": control.session,
                           "seq": 1, "direction": "forward", "speed": 50}).encode()
        sock.chunks.append(packet(0x30, field("prueba/auto/cmd") + move))
        cliente.recibirmensaje()
        self.assertEqual(motor.output, ("forward", 50))

        cliente.publicar("prueba/auto/telemetry", json.dumps(control.snapshot(0)))
        sock.sent = b""
        cliente.recibirmensaje()
        header, body, _ = take_packet(sock.sent)
        self.assertEqual(header, 0x30)
        topic_length = int.from_bytes(body[:2], "big")
        self.assertEqual(json.loads(body[2 + topic_length:])["speed_pct"], 50)
        cliente.cerrar()
        self.assertTrue(sock.closed)
        self.assertFalse(cliente.listo)


class WiFiDouble:
    def __init__(self, conectado=False, conectar_despues=2):
        self.connected = conectado
        self.connecting = False
        self.connect_after = conectar_despues
        self.checks = 0
        self.connect_calls = 0

    def active(self, value):
        self.enabled = value

    def disconnect(self):
        self.connected = False

    def connect(self, ssid, password):
        self.connect_calls += 1
        self.credentials = (ssid, password)
        self.connecting = True

    def isconnected(self):
        if self.connecting:
            self.checks += 1
            if self.connect_after is not None and self.checks >= self.connect_after:
                self.connected = True
        return self.connected

    def ifconfig(self):
        return ("192.0.2.1", "255.255.255.0", "192.0.2.254", "192.0.2.254")


class RedTests(unittest.TestCase):
    def ejecutar(self, wifi, timeout=200):
        reloj = [0]
        servicios = []
        def dormir(ms):
            reloj[0] += ms
        spec = importlib.util.spec_from_file_location("red_prueba", ROOT / "parcial2_wokwi/red.py")
        red = importlib.util.module_from_spec(spec)
        network = types.SimpleNamespace(STA_IF=0, WLAN=lambda _: wifi)
        with patch.dict(sys.modules, {"network": network}):
            with patch.object(time, "sleep_ms", dormir, create=True):
                spec.loader.exec_module(red)
        with patch.object(red, "now_ms", lambda: reloj[0]), patch("builtins.print"):
            try:
                result = red.conectar("Wokwi-GUEST", "", lambda: servicios.append(reloj[0]), timeout)
                return result, servicios, reloj[0]
            except OSError:
                self.assertTrue(servicios)
                self.assertEqual(reloj[0], timeout)
                raise

    def test_devuelve_wifi_y_atiende_parada_durante_espera(self):
        wifi = WiFiDouble()
        result, servicios, _ = self.ejecutar(wifi)
        self.assertIs(result, wifi)
        self.assertEqual(wifi.credentials, ("Wokwi-GUEST", ""))
        self.assertGreater(len(servicios), 1)
        self.assertTrue(result.isconnected())

    def test_conexion_existente_se_reutiliza(self):
        wifi = WiFiDouble(conectado=True)
        result, servicios, tiempo = self.ejecutar(wifi)
        self.assertIs(result, wifi)
        self.assertEqual(wifi.connect_calls, 0)
        self.assertEqual(tiempo, 0)
        self.assertTrue(servicios)

    def test_red_ausente_no_espera_indefinidamente(self):
        with self.assertRaises(OSError):
            self.ejecutar(WiFiDouble(conectar_despues=None))


if __name__ == "__main__":
    unittest.main()
