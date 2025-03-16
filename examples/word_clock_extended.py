# ICON [[(6.59, 7.4), (9.39, 4.6), (1.99, -2.8), (1.99, -12.0), (-2.01, -12.0), (-2.01, -1.2), (6.59, 7.4)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, -2.0)], [(-0.01, 14.0), (1.87, 13.9), (3.1, 13.72), (4.92, 13.27), (6.57, 12.65), (7.85, 12.0), (9.95, 10.56), (11.26, 9.38), (12.07, 8.51), (13.65, 6.4), (14.66, 4.51), (15.18, 3.17), (15.75, 0.9), (15.93, -0.48), (15.99, -2.41), (15.75, -4.87), (15.46, -6.25), (14.87, -8.01), (14.31, -9.23), (13.28, -10.95), (12.42, -12.08), (11.05, -13.55), (9.91, -14.56), (8.05, -15.86), (6.45, -16.69), (4.54, -17.39), (3.36, -17.68), (1.71, -17.92), (0.44, -18.0), (-1.44, -17.94), (-2.97, -17.75), (-5.29, -17.16), (-6.71, -16.59), (-8.07, -15.88), (-10.05, -14.49), (-11.32, -13.34), (-12.48, -12.07), (-13.2, -11.12), (-14.1, -9.69), (-14.72, -8.44), (-15.33, -6.79), (-15.77, -4.91), (-15.98, -3.05), (-16.0, -1.85), (-15.9, -0.04), (-15.44, 2.39), (-14.95, 3.89), (-14.24, 5.45), (-13.24, 7.08), (-12.22, 8.41), (-11.39, 9.31), (-10.07, 10.49), (-8.57, 11.58), (-7.27, 12.32), (-5.83, 12.96), (-4.11, 13.51), (-1.72, 13.91), (-0.06, 14.0)]]
# NAME Word Clock
# DESC No hands!

import time

import machine
import ntptime
import pngdec
from presto import Presto

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)
GRAY = display.create_pen(30, 30, 30)

# Clear the screen before the network call is made
display.set_pen(BLACK)
display.clear()
presto.update()

# Length of time between updates in minutes.
UPDATE_INTERVAL = 1

rtc = machine.RTC()
time_string = None
# 13 characters per line in order of sentence
words = ["it", "d", "is", "m", "about", "l", "a",
         "just", "mid", "nearly",
         "after", "i", "quarter",
         "half", "g", "to", "past", "kl",
         "one", "two", "three", "em",
         "four", "l", "five", "j", "six",
         "eleven", "sg", "ten", "dr",
         "day", "eight", "seven",
         "rm", "twelve", "nine", "c",
         "O'Clock", "w", "night"]


def show_message(text):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH, 2)
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
    nums = {
            0: "twelve", 1: "one", 2: "two",
            3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve"
            }

    if hours == 12 and minutes == 0:
        return "it is mid day"
    if hours == 11 and minutes >= 55 and minutes <= 59:
        return "it is nearly mid day"
    if hours == 12 and minutes >= 1 and minutes <= 5:
        return "it is just after mid day"
    if hours == 00 and minutes == 0:
        return "it is mid night"
    if hours == 23 and minutes >= 55 and minutes <= 59:
        return "it is nearly mid night"
    if hours == 00 and minutes >= 1 and minutes <= 5:
        return "it is just after mid night"
    if hours >= 12:
        hours = hours - 12;
    if minutes == 0:
        return "it is " + nums[hours] + " O'Clock"
    elif minutes == 15:
        return "it is a quarter past " + nums[hours]
    elif minutes == 30:
        return "it is half past " + nums[hours]
    elif minutes == 45:
        return "it is a quarter to " + nums[hours + 1]
    elif minutes > 0 and minutes <= 8:
        return "it is just after " + nums[hours] + " O'Clock"
    elif minutes >= 9 and minutes <= 12:
        return "it is nearly quarter past " + nums[hours]
    elif minutes >= 13 and minutes <= 17:
        return "it is about a quarter past " + nums[hours]
    elif minutes >= 18 and minutes <= 22:
        return "it is just after quarter past " + nums[hours]
    elif minutes >= 23 and minutes <= 27:
        return "it is nearly half past " + nums[hours]
    elif minutes >= 28 and minutes <= 32:
        return "it is about half past " + nums[hours]
    elif minutes >= 33 and minutes <= 38:
        return "it is just after half past " + nums[hours]
    elif minutes >= 39 and minutes <= 42:
        return "it is nearly quarter to " + nums[hours + 1]
    elif minutes >= 43 and minutes <= 47:
        return "it is about a quarter to " + nums[hours + 1]
    elif minutes >= 48 and minutes <= 54:
        return "it is just after quarter to %s" % nums[hours + 1]
    elif minutes >= 55 and minutes <= 59:
        return "it is nearly " + nums[hours + 1] + " O'Clock"
    else:
        return "it is %s %s" % (nums[hours], nums[minutes])


def update():
    global time_string
    # grab the current time from the ntp server and update the Pico RTC
    try:
        ntptime.settime()
    except OSError:
        print("Unable to contact NTP server")

    current_t = rtc.datetime()
    time_string = approx_time(current_t[4], current_t[5])

    # Splits the string into an array of words for displaying later
    time_string = time_string.split()

    print(time_string)


def draw():
    global time_string
    display.set_font("bitmap8")

    display.set_layer(1)

    # Clear the screen
    display.set_pen(BLACK)
    display.clear()

    default_x = 25
    x = default_x
    y = 25

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

    presto.update()


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

