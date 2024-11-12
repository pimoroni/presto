'''

SD Card example showing the writing and reading back of a text file.

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

    # Open the file in write mode, if the file doesn't exist it will create it
    f = open('sd/presto.txt', 'w')
    # Write the string to the file we opened above
    f.write("Hello from Pimoroni Presto!")
    # Once we're done writing to the file we can close it.
    f.close()

    # Now lets read the file back and print the content to the terminal!
    # This opens the file in read only mode
    f = open('sd/presto.txt')

    # Read the content and store it in a variable
    data = f.read()

    # And now we're done, close the file
    f.close()

    # Finally, we'll print the content we stored in our data variable
    print("Here is the content from our file:\n\n{}".format(data))
except OSError as e:
    print(e)
