import time

import machine
import network
import ntptime
import pngdec
from picographics import DISPLAY_PRESTO, PicoGraphics
from presto import Presto

machine.freq(264000000)

# Check and import the Network SSID and Password from secrets.py
# import the Spotify API keys from that file too
try:
    from secrets import WIFI_PASSWORD, WIFI_SSID
    if WIFI_SSID == "":
        raise ValueError("WIFI_SSID in 'secrets.py' is empty!")
    if WIFI_PASSWORD == "":
        raise ValueError("WIFI_PASSWORD in 'secrets.py' is empty!")
except ImportError:
    raise ImportError("'secrets.py' is missing from your Plasma 2350 W!")
except ValueError as e:
    print(e)

# Length of time between updates in minutes.
UPDATE_INTERVAL = 15
display = None

rtc = machine.RTC()
time_string = None
words = ["it", "d", "is", "m", "about", "lv", "half", "c", "quarter", "b", "to", "past", "n", "one",
         "two", "three", "four", "five", "six", "eleven", "ten", "d", "nin", "eight", "seven", "rm", "twelve", "rtywtqdj", "O'Clock", "grd", "nhelloprestoa"]

wlan = network.WLAN(network.STA_IF)


def network_connect():
    # Connect to the network specified in secrets.py
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    attempts = 0
    while wlan.isconnected() is False:
        print("Attempting connection to {}".format(WIFI_SSID))
        time.sleep(1)
        attempts += 1
        if attempts > 10:
            raise OSError('Unable to connect to wireless network. Check your WIFI_SSID and WIFI_PASSWORD and try again.')


# Start connection to the network
network_connect()

# Store the local IP address
ip_addr = wlan.ipconfig('addr4')[0]

# Let the user know the connection has been successful
# and display the current IP address of the Pimoroni Presto
print("Successfully connected to {}. Your Pimoroni Presto IP is: {}".format(WIFI_SSID, ip_addr))

# Set the correct time using the NTP service.
ntptime.settime()

# Setup for the Presto display
presto = Presto()
display = PicoGraphics(DISPLAY_PRESTO, buffer=memoryview(presto), layers=2)
WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)
GRAY = display.create_pen(30, 30, 30)


def approx_time(hours, minutes):
    nums = {0: "twelve", 1: "one", 2: "two",
            3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve"}

    if hours == 12:
        hours = 0
    if minutes > 0 and minutes < 8:
        return "it is about " + nums[hours] + " O'Clock"
    elif minutes >= 8 and minutes < 23:
        return "it is about quarter past " + nums[hours]
    elif minutes >= 23 and minutes < 38:
        return "it is about half past " + nums[hours]
    elif minutes >= 38 and minutes < 53:
        return "it is about quarter to " + nums[hours + 1]
    else:
        return "it is about " + nums[hours + 1] + " O'Clock"


def update():
    global time_string
    # grab the current time from the ntp server and update the Pico RTC
    try:
        ntptime.settime()
    except OSError:
        print("Unable to contact NTP server")

    current_t = rtc.datetime()
    time_string = approx_time(current_t[4] - 12 if current_t[4] > 12 else current_t[4], current_t[5])

    # Splits the string into an array of words for displaying later
    time_string = time_string.split()

    print(time_string)


def draw():
    global time_string
    display.set_font("bitmap8")

    WIDTH, HEIGHT = display.get_bounds()

    display.set_layer(1)

    # Clear the screen
    display.set_pen(BLACK)
    display.clear()

    default_x = 25
    x = default_x
    y = 35

    line_space = 20
    letter_space = 15
    margin = 25
    scale = 1
    spacing = 1

    for word in words:

        if word in time_string:
            display.set_pen(WHITE)
        else:
            display.set_pen(GRAY)

        for letter in word:
            text_length = display.measure_text(letter, scale, spacing)
            if not x + text_length <= WIDTH - margin:
                y += line_space
                x = default_x

            display.text(letter.upper(), x, y, WIDTH, scale=scale, spacing=spacing)
            x += letter_space

    presto.update(display)


# Set the background in layer 0
# This means we don't need to decode the image every frame

display.set_layer(0)

try:
    p = pngdec.PNG(display)

    p.open_file("wordclock_background.png")
    p.decode(0, 0)
except OSError:
    display.set_pen(BLACK)
    display.clear()


while True:
    update()
    draw()
    time.sleep(60 * UPDATE_INTERVAL)
