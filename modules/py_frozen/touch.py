from micropython import const
from machine import I2C, Pin
import math


class FT6236:
    TOUCH_INT = const(32)
    TOUCH_I2C = const(1)
    TOUCH_SDA = const(30)
    TOUCH_SCL = const(31)
    TOUCH_ADDR = const(0x48)

    STATE_DOWN = const(0b00)
    STATE_UP = const(0b01)
    STATE_CONTACT = const(0b10)
    STATE_NONE = const(0b11)

    def __init__(self, enable_interrupt=False):
        self.debug = False
        self._irq = enable_interrupt

        self.x = 120
        self.y = 120
        self.state = False

        self.x2 = 120
        self.y2 = 120
        self.state2 = False

        self.distance = 0
        self.angle = 0

        self._buf = bytearray(15)
        self._data = memoryview(self._buf)

        self._i2c = I2C(self.TOUCH_I2C, sda=Pin(self.TOUCH_SDA), scl=Pin(self.TOUCH_SCL))
        self._touch_int = Pin(self.TOUCH_INT, Pin.IN, Pin.PULL_UP)

        if self._irq:
            self._touch_int.irq(self._handle_touch, trigger=Pin.IRQ_FALLING)

    def poll(self):
        if self._irq:
            return None

        if not self._touch_int.value() or self.state or self.state2:
            self.handle_touch(self._touch_int)

    def _read_touch(self, data):
        e = data[0] >> 6
        x = ((data[0] & 0x0f) << 8) | data[1]
        y = ((data[2] & 0x0f) << 8) | data[3]
        return int(x / 2), int(y / 2), e not in (self.STATE_NONE, self.STATE_UP)

    def _handle_touch(self, pin):
        self.state = self.state2 = False

        self._i2c.writeto(self.TOUCH_ADDR, b'\x00', False)
        self._i2c.readfrom_into(self.TOUCH_ADDR, self._buf)

        mode, gesture, touches = self._data[:3]
        touches &= 0x0f

        for n in range(touches):
            data = self._data[3 + n * 6:]
            touch_id = data[2] >> 4
            if touch_id == 0:
                self.x, self.y, self.state = self._read_touch(data)
            else:
                self.x2, self.y2, self.state2 = self._read_touch(data)

        if self.state and self.state2:
            self.distance = math.sqrt(abs(self.x2 - self.x)**2 + abs(self.y2 - self.y)**2)
            self.angle = math.degrees(math.atan2(self.y2 - self.y, self.x2 - self.x)) + 180

        if self.debug:
            print(self.x, self.y, self.x2, self.y2, self.distance, self.angle, self.state, self.state2)
