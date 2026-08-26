import machine
import sdcard
import uos
from picovector import color, font, image

from presto import Presto

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height

display.font = font.load("Roboto-Medium.af")


# Couple of pens for clearing the screen and text.
WHITE = color.rgb(255, 255, 255)
BLACK = color.rgb(0, 0, 0)

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
    display.pen = WHITE
    display.clear()

    # Add some text
    display.pen = BLACK
    display.text("Image loaded from SD:", 10, 10, 16)

    # Open the JPEG file
    picture = image.load("sd/micro_sd.jpg")

    # Decode the JPEG
    display.blit(picture, 10, 40)

    # Finally we update the screen with our changes :)
    presto.update()
