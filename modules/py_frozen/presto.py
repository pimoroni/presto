import asyncio
import _presto
from touch import FT6236
from backlight import Reactive
from ezwifi import EzWiFi

from collections import namedtuple
from picographics import PicoGraphics, DISPLAY_PRESTO, DISPLAY_PRESTO_FULL_RES, PEN_RGB565, PEN_P8


Touch = namedtuple("touch", ("x", "y", "touched"))


class Presto():
    NUM_LEDS = 7
    LED_PIN = 33

    def __init__(self, full_res=False, palette=False, ambient_light=False, direct_to_fb=False, layers=None):
        # WiFi - *must* happen before Presto bringup
        # Note: Forces WiFi details to be in secrets.py
        self.wifi = EzWiFi()

        # Touch Input
        self.touch = FT6236(full_res=full_res)

        # Display Driver & PicoGraphics
        if layers is None:
            layers = 1 if full_res else 2
        pen = PEN_P8 if palette else PEN_RGB565
        self.presto = _presto.Presto(full_res=full_res, palette=palette)
        self.buffer = None if (full_res and not palette and not direct_to_fb) else memoryview(self.presto)
        self.display = PicoGraphics(DISPLAY_PRESTO_FULL_RES if full_res else DISPLAY_PRESTO, buffer=self.buffer, layers=layers, pen_type=pen)
        self.width, self.height = self.display.get_bounds()

        if ambient_light:
            self.presto.auto_ambient_leds(True)

    @property
    def touch_a(self):
        return Touch(self.touch.x, self.touch.y, self.touch.state)

    @property
    def touch_b(self):
        return Touch(self.touch.x2, self.touch.y2, self.touch.state2)

    @property
    def touch_delta(self):
        return self.touch.distance, self.touch.angle

    async def async_connect(self):
        await self.wifi.connect()

    def set_backlight(self, brightness):
        self.presto.set_backlight(brightness)

    def auto_ambient_leds(self, enable):
        self.presto.auto_ambient_leds(enable)

    def connect(self, ssid=None, password=None):
        return asyncio.get_event_loop().run_until_complete(self.wifi.connect(ssid, password))

    def touch_poll(self):
        self.touch.poll()

    def update(self):
        self.presto.update(self.display)
        self.touch.poll()

    def partial_update(self, x, y, w, h):
        self.presto.partial_update(self.display, x, y, w, h)
        self.touch.poll()

    def clear(self):
        self.display.clear()
        self.presto.update(self.display)
