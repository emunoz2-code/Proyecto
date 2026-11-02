import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "parcial2_wokwi"))
import config
from mqtt_wire import MQTTClient, field, packet, take_packet


class SocketDouble:
    def __init__(self, chunks=(), send_limit=10000):
        self.chunks = list(chunks)
        self.sent = b""
        self.send_limit = send_limit
        self.closed = False

    def send(self, data):
        count = min(len(data), self.send_limit)
        self.sent += data[:count]
        return count

    def recv(self, count):
        if not self.chunks:
            raise BlockingIOError(11, "would block")
        return self.chunks.pop(0)

    def close(self):
        self.closed = True

    def settimeout(self, timeout):
        self.timeout = timeout

    def setblocking(self, value):
        self.blocking = value

    def connect(self, address):
        self.address = address

    def sendall(self, data):
        self.sent += data


class MQTTTests(unittest.TestCase):
    def setUp(self):
        self.messages = []
        self.client = MQTTClient(config, lambda *args: self.messages.append(args))
        self.client.ready = True

    def test_variable_length_and_fragments(self):
        encoded = packet(0x30, b"x" * 300)
        for index in range(len(encoded)):
            self.assertIsNone(take_packet(encoded[:index]))
        self.assertEqual(take_packet(encoded)[1], b"x" * 300)

    def test_oversized_frame_rejected(self):
        with self.assertRaises(OSError):
            take_packet(b"\x30\xff\x7f")

    def test_invalid_remaining_length(self):
        with self.assertRaises(OSError):
            take_packet(b"\x30\x80\x80\x80\x80")

    def test_retained_bit_passed_to_controller(self):
        body = field("base/cmd") + b"{}"
        self.client.handle(0x31, body)
        self.assertEqual(self.messages, [("base/cmd", b"{}", True)])

    def test_qos1_rejected(self):
        with self.assertRaises(OSError):
            self.client.handle(0x32, field("cmd") + b"\x00\x01{}")

    def test_invalid_topic_length(self):
        with self.assertRaises(OSError):
            self.client.handle(0x30, b"\x00\xffa")

    def test_subscription_rejection(self):
        with self.assertRaises(OSError):
            self.client.handle(0x90, b"\x00\x01\x80")

    def test_fragmented_tcp_and_partial_send(self):
        data = packet(0x30, field("base/cmd") + b"{}")
        sock = SocketDouble([data[:3], data[3:8], data[8:]], send_limit=2)
        self.client.sock = sock
        self.client.enqueue(b"abcdef")
        for _ in range(3):
            self.client.poll()
        self.assertEqual(sock.sent, b"abcdef")
        self.assertEqual(self.messages, [("base/cmd", b"{}", False)])

    def test_closed_socket_detected(self):
        self.client.sock = SocketDouble([b""])
        with self.assertRaises(OSError):
            self.client.poll()

    def test_partial_packet_timeout(self):
        self.client.sock = SocketDouble()
        self.client.partial_at = 0
        with patch("mqtt_wire.now_ms", return_value=500):
            with self.assertRaises(OSError):
                self.client.poll()

    def test_send_timeout(self):
        self.client.sock = SocketDouble()
        self.client.tx = [[b"abc", 0]]
        with patch("mqtt_wire.now_ms", return_value=1000):
            with self.assertRaises(OSError):
                self.client.poll()

    def test_ping_timeout(self):
        self.client.sock = SocketDouble()
        self.client.ping_at = 0
        with patch("mqtt_wire.now_ms", return_value=3000):
            with self.assertRaises(OSError):
                self.client.poll()

    def test_queue_is_bounded(self):
        with self.assertRaises(OSError):
            self.client.enqueue(b"x" * 4097)

    def test_connect_will_credentials_and_subscription(self):
        sock = SocketDouble([b"\x20", b"\x02\x00\x00"])
        with patch("mqtt_wire.socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 1883))]):
            with patch("mqtt_wire.socket.socket", return_value=sock):
                self.client.connect("test-device", "base/car")
        header, body, _ = take_packet(sock.sent)
        self.assertEqual(header, 0x10)
        self.assertEqual(body[:7], b"\x00\x04MQTT\x04")
        self.assertEqual(body[7], 0x26)  # clean session y Will retain; sin credenciales.
        self.assertIn(field("base/car/availability"), body)
        self.assertIn(b'{"v":1,"online":false}', body)
        self.assertFalse(sock.blocking)
        self.assertFalse(self.client.ready)
        self.assertEqual(take_packet(self.client.tx[0][0])[1], b"\x00\x01" + field("base/car/cmd") + b"\x00")
        self.client.handle(0x90, b"\x00\x01\x00")
        self.assertTrue(self.client.ready)

    def test_connect_rejection_closes_socket(self):
        sock = SocketDouble([b"\x20\x02\x00\x05"])
        with patch("mqtt_wire.socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 1883))]):
            with patch("mqtt_wire.socket.socket", return_value=sock):
                with self.assertRaises(OSError):
                    self.client.connect("test", "base")
        self.assertTrue(sock.closed)
        self.assertIsNone(self.client.sock)


if __name__ == "__main__":
    unittest.main()
