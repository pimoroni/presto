# ICON schedule
# NAME Word Clock
# DESC No hands!

import time

import ntptime
from picovector import color, font, image

from presto import Presto

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height

display.font = font.load("Roboto-Medium.af")
LETTER_SIZE = 12
BLACK = color.rgb(0, 0, 0)
WHITE = color.rgb(200, 200, 200)
GRAY = color.rgb(30, 30, 30)

# Clear the screen before the network call is made
display.pen = BLACK
display.clear()
presto.update()

# Length of time between updates in minutes.
UPDATE_INTERVAL = 15
# Hours offset from UTC, set once in secrets.py
try:
    from secrets import UTC_OFFSET
except ImportError:
    UTC_OFFSET = 0

time_string = None
words = ["it", "d", "is", "m", "about", "lv", "half", "c", "quarter", "b", "to", "past", "n", "one",
         "two", "three", "four", "five", "six", "eleven", "ten", "d", "qdh", "eight", "seven", "rm", "twelve", "nine", "p", "ncsnheypresto", "O'Clock", "agrdsp"]


def show_message(text):
    display.pen = BLACK
    display.clear()
    display.pen = WHITE
    display.text(f"{text}", 5, 10, 16)
    presto.update()


show_message("Connecting...")

try:
    wifi = presto.connect()
except ValueError as e:
    while True:
        show_message(e)
except ImportError as e:
    while True:
        show_message(e)

# Set the correct time using the NTP service.
try:
    ntptime.settime()
except OSError:
    while True:
        show_message("Unable to get time.\n\nCheck your network try again.")


def approx_time(hours, minutes):
    nums = {0: "twelve", 1: "one", 2: "two",
            3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve"}

    if hours == 12:
        hours = 0

    if minutes >= 0 and minutes < 8:
        return "it is about " + nums[hours] + " O'Clock"

    if minutes >= 8 and minutes < 23:
        return "it is about quarter past " + nums[hours]

    if minutes >= 23 and minutes < 38:
        return "it is about half past " + nums[hours]

    if minutes >= 38 and minutes < 53:
        return "it is about quarter to " + nums[hours + 1]

    return "it is about " + nums[hours + 1] + " O'Clock"


def update():
    global time_string
    # grab the current time from the ntp server and update the Pico RTC
    try:
        ntptime.settime()
    except OSError:
        print("Unable to contact NTP server")

    current_t = time.gmtime(time.time() + UTC_OFFSET * 3600)
    adjusted_hr, adjusted_min = current_t[3], current_t[4]

    time_string = approx_time(adjusted_hr - 12 if adjusted_hr > 12 else adjusted_hr, adjusted_min)

    # Splits the string into an array of words for displaying later
    time_string = time_string.split()

    print(time_string)


def draw():
    global time_string

    # The background is decoded once and blitted each frame; there are no
    # layers to keep it on.
    if background is None:
        display.pen = BLACK
        display.clear()
    else:
        display.blit(background, 0, 0)

    default_x = 25
    x = default_x
    y = 35

    line_space = 20
    letter_space = 15
    margin = 25

    for word in words:

        if word in time_string:
            display.pen = WHITE
        else:
            display.pen = GRAY
        for letter in word:
            text_length = display.measure_text(letter.upper(), LETTER_SIZE)[0]
            if not x + text_length <= WIDTH - margin:
                y += line_space
                x = default_x

            display.text(letter.upper(), x, y, LETTER_SIZE)
            x += letter_space

    presto.update()


# Decode the background once, rather than every frame
try:
    background = image.load("wordclock_background.png")
except OSError:
    background = None


while True:
    update()
    draw()
    time.sleep(60 * UPDATE_INTERVAL)
