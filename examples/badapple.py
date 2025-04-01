from time import ticks_us

import machine
import micropython
from picographics import DISPLAY_PRESTO, PicoGraphics
from presto import Presto

machine.freq(264000000)

import machine
import sdcard
import uos

try:
    # Setup for SD Card
    sd_spi = machine.SPI(0, baudrate=66_000_000, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")

except OSError as e:
    print(e)

# Setup for the Presto display
presto = Presto()
display = PicoGraphics(DISPLAY_PRESTO, buffer=memoryview(presto))
WIDTH, HEIGHT = display.get_bounds()

# Read the bad apple video file from the SD card
video = open(f"/sd/badapple{WIDTH}x{HEIGHT}.bin", "rb")

y = 0
x = 0
tick_increment = 1000000 // 30
next_tick = ticks_us()

# This Micropython Viper function is compiled to native code
# for maximum execution speed.
@micropython.viper
def render(data:ptr8, x:int, y:int, next_tick:int):  # noqa: F821
    for i in range(0, 1024, 2):
        # The encoded video data is an array of span lengths and
        # greyscale colour values
        span_len = int(data[i])
        colour = int(data[i+1])

        # Expand the grey colour to each colour channel
        colour = (colour << 11) | (colour << 6) | colour

        # Byte swap for the display
        colour = (colour & 0xFF) << 8 | (colour >> 8)

        display.set_pen(colour)
        display.pixel_span(x, y, span_len)

        x += span_len
        if x >= 240:
            y += 1
            x = 0
            if y >= 240:
                presto.update(display)

                # Wait until the next frame at 15FPS
                next_tick += 1000000 // 15
                while int(ticks_us()) < next_tick:
                    pass
                y = 0

    return x, y, next_tick

# Read out the file and render
while True:
    data = video.read(1024)
    if len(data) < 1024: break
    x, y, next_tick = render(data, x, y, next_tick)
