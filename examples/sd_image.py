import sdcard
import machine
import uos
import jpegdec
from picographics import PicoGraphics, DISPLAY_PRESTO
from presto import Presto

# Setup for the Presto display
portal = Presto()
display = PicoGraphics(DISPLAY_PRESTO, buffer=memoryview(portal))
WIDTH, HEIGHT = display.get_bounds()

j = jpegdec.JPEG(display)

# Couple of pens for clearing the screen and text.
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

try:
    # Setup for SD Card
    sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")
except OSError as e:
    print(e)


while True:
    # Clear the screen
    display.set_pen(WHITE)
    display.clear()

    # Add some text
    display.set_pen(BLACK)
    display.text("Image loaded from SD:", 10, 10, WIDTH, 2)

    # Open the JPEG file
    j.open_file("sd/micro_sd.jpg")

    # Decode the JPEG
    j.decode(10, 40, jpegdec.JPEG_SCALE_FULL, dither=True)

    # Finally we update the screen with our changes :)
    portal.update(display)
