"""MQTT 3.1.1 mínimo, QoS 0, TCP para la simulación. Sin TLS.

Solo connect() bloquea y se llama con motores detenidos. poll() procesa una
cantidad limitada de bytes/paquetes y conserva fragmentos TCP entre ciclos.
"""
import socket
from clockutil import now_ms, elapsed

MAX_PACKET = 1024
MAX_QUEUE = 4096
IO_DEADLINE_MS = 1000
PARTIAL_DEADLINE_MS = 500
WOULD_BLOCK = (11, 35, 10035, 115, 119)


def field(value):
    if isinstance(value, str):
        value = value.encode()
    length = len(value)
    if length > 65535:
        raise ValueError("Campo MQTT demasiado largo")
    return bytes((length >> 8, length & 255)) + value


def packet(header, body=b""):
    length = len(body)
    if length > MAX_PACKET:
        raise ValueError("Paquete MQTT demasiado largo")
    encoded = bytearray((header,))
    while True:
        digit = length % 128
        length //= 128
        encoded.append(digit | (128 if length else 0))
        if not length:
            break
    return bytes(encoded) + body


def take_packet(buf):
    """Devuelve (header, body, bytes_usados) o None para fragmento incompleto."""
    if len(buf) < 2:
        return None
    length, multiplier = 0, 1
    for index in range(1, 5):
        if index >= len(buf):
            return None
        value = buf[index]
        length += (value & 127) * multiplier
        if length > MAX_PACKET:
            raise OSError("MQTT excede el límite")
        if value & 128 == 0:
            end = index + 1 + length
            if len(buf) < end:
                return None
            return buf[0], bytes(buf[index + 1:end]), end
        multiplier *= 128
    raise OSError("Longitud MQTT inválida")


class MQTTClient:
    def __init__(self, cfg, callback):
        self.cfg, self.callback = cfg, callback
        self.sock = None
        self.rx, self.tx = bytearray(), []
        self.partial_at = None
        self.ping_at = None
        self.last_ping = now_ms()
        self.started = now_ms()
        self.ready = False

    def connect(self, client_id, base):
        self.close()
        cfg = self.cfg
        address = socket.getaddrinfo(cfg.MQTT_HOST, cfg.MQTT_PORT, socket.AF_INET, socket.SOCK_STREAM)[0][-1]
        self.sock = socket.socket()
        self.sock.settimeout(cfg.CONNECT_TIMEOUT_S)
        try:
            self.sock.connect(address)
            # Clean session + Will QoS0 + Will retain.
            flags = 0x26
            payload = field(client_id) + field(base + "/availability") + field(b'{"v":1,"online":false}')
            if cfg.MQTT_USER:
                flags |= 0xC0
                payload += field(cfg.MQTT_USER) + field(cfg.MQTT_PASSWORD)
            keepalive = cfg.MQTT_KEEPALIVE_S
            body = b"\x00\x04MQTT\x04" + bytes((flags, keepalive >> 8, keepalive & 255)) + payload
            self.sock.sendall(packet(0x10, body))
            response = b""
            while len(response) < 4:
                chunk = self.sock.recv(4 - len(response))
                if not chunk:
                    raise OSError("Broker cerró durante CONNACK")
                response += chunk
            if response != b"\x20\x02\x00\x00":
                raise OSError("CONNACK rechazado o inválido: %r" % response)
            self.sock.setblocking(False)
            self.started = self.last_ping = now_ms()
            self.enqueue(packet(0x82, b"\x00\x01" + field(base + "/cmd") + b"\x00"))
        except Exception:
            self.close()
            raise

    def enqueue(self, data):
        if sum(len(item[0]) for item in self.tx) + len(data) > MAX_QUEUE:
            raise OSError("Cola MQTT llena")
        self.tx.append([data, now_ms()])

    def publish(self, topic, payload, retain=False):
        if isinstance(payload, str):
            payload = payload.encode()
        self.enqueue(packet(0x31 if retain else 0x30, field(topic) + payload))

    def handle(self, header, body):
        kind = header >> 4
        if kind == 9:
            if header != 0x90 or body != b"\x00\x01\x00":
                raise OSError("SUBACK inválido o suscripción rechazada")
            self.ready = True
        elif kind == 3:
            if not self.ready or header & 6:
                raise OSError("Solo PUBLISH QoS0 después de SUBACK")
            if len(body) < 2:
                raise OSError("PUBLISH incompleto")
            length = (body[0] << 8) | body[1]
            if not length or length + 2 > len(body):
                raise OSError("Topic inválido")
            topic = body[2:2 + length].decode()
            self.callback(topic, body[2 + length:], bool(header & 1))
        elif header == 0xD0 and not body:
            self.ping_at = None
        else:
            raise OSError("Paquete MQTT no admitido")

    def poll(self):
        now = now_ms()
        if not self.sock:
            raise OSError("Sin socket")
        if not self.ready and elapsed(now, self.started) >= 3000:
            raise OSError("SUBACK timeout")
        if self.partial_at is not None and elapsed(now, self.partial_at) >= PARTIAL_DEADLINE_MS:
            raise OSError("Paquete TCP incompleto: timeout")
        if self.tx:
            data, started = self.tx[0]
            if elapsed(now, started) >= IO_DEADLINE_MS:
                raise OSError("Envío MQTT: timeout")
            try:
                count = self.sock.send(data)
                if count == 0:
                    raise OSError("Socket cerrado al enviar")
                if count:
                    if count == len(data):
                        self.tx.pop(0)
                    else:
                        self.tx[0][0] = data[count:]
            except OSError as exc:
                if not exc.args or exc.args[0] not in WOULD_BLOCK:
                    raise
        try:
            chunk = self.sock.recv(256)
            if chunk == b"":
                raise OSError("Broker desconectado")
            if chunk:
                self.rx.extend(chunk)
        except OSError as exc:
            if not exc.args or exc.args[0] not in WOULD_BLOCK:
                raise
        if len(self.rx) > MAX_PACKET + 260:
            raise OSError("Búfer MQTT excedido")
        for _ in range(4):
            decoded = take_packet(self.rx)
            if decoded is None:
                break
            header, body, count = decoded
            del self.rx[:count]
            self.partial_at = None
            self.handle(header, body)
        if self.rx and self.partial_at is None:
            self.partial_at = now
        if not self.rx:
            self.partial_at = None
        if self.ping_at is not None and elapsed(now, self.ping_at) >= 3000:
            raise OSError("PINGRESP timeout")
        if self.ready and self.ping_at is None and elapsed(now, self.last_ping) >= self.cfg.MQTT_KEEPALIVE_S * 500:
            self.enqueue(b"\xc0\x00")
            self.last_ping = self.ping_at = now

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self.ready = False
        self.rx = bytearray()
        self.tx = []
        self.partial_at = self.ping_at = None
