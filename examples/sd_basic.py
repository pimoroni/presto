'''

An example to show how to setup the SD Card slot and list the files in the root dir

'''
import sdcard
import machine
import uos

try:
    # Setup for SD Card
    sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")

    # Print a list of the files on the root of the SD
    print(uos.listdir('sd'))

except OSError as e:
    print(e)
