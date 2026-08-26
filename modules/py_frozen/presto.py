import asyncio
from collections import namedtuple

import _presto
from ezwifi import EzWiFi
from machine import PWM, Pin
from picovector import image
from touch import FT6236

Touch = namedtuple("touch", ("x", "y", "touched"))

# The ST7701 scans the framebuffer out line by line, so only a 180 flip is
# possible - 90/270 would need a transpose the scanout cannot do.
ROTATE_0 = 0
ROTATE_180 = 180


class Buzzer:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))

    def set_tone(self, freq, duty=0.5):
        if freq < 50.0:  # uh... https://github.com/micropython/micropython/blob/af64c2ddbd758ab6bac0fcca94c66d89046663be/ports/rp2/machine_pwm.c#L105-L119
            self.pwm.duty_u16(0)
            return False

        self.pwm.freq(freq)
        self.pwm.duty_u16(int(65535 * duty))
        return True


class Presto():
    NUM_LEDS = 7
    LED_PIN = 33

    def __init__(self, full_res=False, ambient_light=False, rotate=ROTATE_0):
        # WiFi - *must* happen before Presto bringup
        # Note: Forces WiFi details to be in secrets.py
        self.wifi = EzWiFi()

        # Touch Input
        self.touch = FT6236(full_res=full_res, rotate=rotate)

        self.presto = _presto.Presto(full_res=full_res, rotate=rotate)
        self.width = 480 if full_res else 240
        self.height = 480 if full_res else 240

        # The C module hands out its RGBA8888 drawing surface; picovector
        # rasterises straight into it and update() converts it for scanout.
        self.display = image(self.width, self.height, memoryview(self.presto))

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

    def set_led_rgb(self, i, r, g, b):
        self.presto.set_led_rgb(i, r, g, b)

    def set_led_hsv(self, i, h, s, v):
        self.presto.set_led_hsv(i, h, s, v)

    def connect(self, ssid=None, password=None):
        return asyncio.get_event_loop().run_until_complete(self.wifi.connect(ssid, password))

    def touch_poll(self):
        self.touch.poll()

    def update(self):
        self.presto.update()
        self.touch.poll()

    def partial_update(self, x, y, w, h):
        self.presto.partial_update(x, y, w, h)
        self.touch.poll()

    def clear(self):
        self.display.clear()
        self.presto.update()
