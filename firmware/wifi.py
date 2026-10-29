"""Las esperas de conexión solo se hacen con motores deshabilitados."""
import network
from time import sleep_ms
from clockutil import now_ms, elapsed


class WiFi:
    def __init__(self, cfg):
        self.cfg = cfg
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connected(self):
        return self.wlan.isconnected()

    def connect(self, service_safe):
        if self.connected():
            return
        try:
            self.wlan.disconnect()
        except OSError:
            pass
        self.wlan.connect(self.cfg.WIFI_SSID, self.cfg.WIFI_PASSWORD)
        start = now_ms()
        while not self.connected():
            service_safe()
            if elapsed(now_ms(), start) >= self.cfg.WIFI_TIMEOUT_MS:
                raise OSError("Wi-Fi timeout")
            sleep_ms(50)
