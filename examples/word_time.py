# ICON [[(6.59, 7.4), (9.39, 4.6), (1.99, -2.8), (1.99, -12.0), (-2.01, -12.0), (-2.01, -1.2), (6.59, 7.4)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, -2.0)], [(-0.01, 14.0), (1.87, 13.9), (3.1, 13.72), (4.92, 13.27), (6.57, 12.65), (7.85, 12.0), (9.95, 10.56), (11.26, 9.38), (12.07, 8.51), (13.65, 6.4), (14.66, 4.51), (15.18, 3.17), (15.75, 0.9), (15.93, -0.48), (15.99, -2.41), (15.75, -4.87), (15.46, -6.25), (14.87, -8.01), (14.31, -9.23), (13.28, -10.95), (12.42, -12.08), (11.05, -13.55), (9.91, -14.56), (8.05, -15.86), (6.45, -16.69), (4.54, -17.39), (3.36, -17.68), (1.71, -17.92), (0.44, -18.0), (-1.44, -17.94), (-2.97, -17.75), (-5.29, -17.16), (-6.71, -16.59), (-8.07, -15.88), (-10.05, -14.49), (-11.32, -13.34), (-12.48, -12.07), (-13.2, -11.12), (-14.1, -9.69), (-14.72, -8.44), (-15.33, -6.79), (-15.77, -4.91), (-15.98, -3.05), (-16.0, -1.85), (-15.9, -0.04), (-15.44, 2.39), (-14.95, 3.89), (-14.24, 5.45), (-13.24, 7.08), (-12.22, 8.41), (-11.39, 9.31), (-10.07, 10.49), (-8.57, 11.58), (-7.27, 12.32), (-5.83, 12.96), (-4.11, 13.51), (-1.72, 13.91), (-0.06, 14.0)]]
# NAME Word Time
# DESC Time shown as words

import time
import ntptime

from presto import Presto
from touch import Button
from picovector import ANTIALIAS_BEST, PicoVector, Polygon


class button():
    def __init__(self, display, vector, text, bg, fg, x, y, h, w, r = 0):
        self.display = display
        self.vector = vector
        self.text = text
        self.bg = bg
        self.fg = fg
        self.button = Button(x, y, h, w)
        self.polygon = Polygon()
        self.polygon.rectangle(x, y, h, w, (r, r, r, r))
    
    
    def draw(self):
        self.display.set_pen(self.bg)
        self.vector.draw(self.polygon)

        self.vector.set_font_size(20)
        self.display.set_pen(self.fg)
        x_text, y_text, w_text, h_text = self.vector.measure_text(self.text)
        x_offset = int((self.button.bounds[2] - w_text) / 2) + self.button.bounds[0]
        y_offset = int(((self.button.bounds[3] - h_text) / 2) + self.button.bounds[1] + h_text)
        self.vector.text(self.text, x_offset, y_offset)
    
    
    def pressed(self):
        return self.button.is_pressed()


def show_message(text):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


def approx_time(hours, minutes):
    nums = {0: "twelve", 1: "one", 2: "two",
            3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve"}

    if hours == 12:
        hours = 0
    if minutes >= 0 and minutes < 3:
        return (nums[hours], "O'Clock", "")
    elif minutes >= 3 and minutes < 8:
        return ("five", "past", nums[hours])
    elif minutes >= 8 and minutes < 13:
        return ("ten", "past", nums[hours])
    elif minutes >= 13 and minutes < 18:
        return ("quarter", "past", nums[hours])
    elif minutes >= 18 and minutes < 23:
        return ("twenty", "past", nums[hours])
    elif minutes >= 23 and minutes < 28:
        return ("twenty five", "past", nums[hours])
    elif minutes >= 28 and minutes < 33:
        return ("half", "past", nums[hours])
    elif minutes >= 33 and minutes < 38:
        return ("twenty five", "to", nums[hours + 1])
    elif minutes >= 38 and minutes < 43:
        return ("twenty", "to", nums[hours + 1])
    elif minutes >= 43 and minutes < 48:
        return ("quarter", "to", nums[hours + 1])
    elif minutes >= 48 and minutes < 53:
        return ("ten", "to", nums[hours + 1])
    elif minutes >=53 and minutes < 58:
        return ("five", "to", nums[hours + 1])
    else:
        return (nums[hours + 1], "O'Clock", "")


def update():
    
    current_t = time.gmtime(time.time() + UTC_OFFSET * 3600)
    time_phrase = approx_time(current_t[3] - 12 if current_t[3] > 12 else current_t[3], current_t[4])

    print(current_t, time_phrase)
    
    return time_phrase


def draw(time_phrase):
    display.set_font("bitmap8")

    display.set_pen(BLACK)
    display.clear()

    default_x = 25
    x = default_x
    y = 40

    line_space = 40
    letter_space = 15
    margin = 25
    scale = 1
    spacing = 1

    display.set_pen(WHITE)
    
    header = "IT IS ABOUT"
    vector.set_font_size(25)
    x_text, y_text, w_text, h_text = vector.measure_text(header)
    x_offset = int((WIDTH - w_text) / 2)
    vector.text(header, x_offset, y)
    
    y += line_space + 15
    vector.set_font_size(40)
    for line in time_phrase:
        line = line.upper()
#        x_offset = int((WIDTH - display.measure_text(line, scale = 3, spacing = 3)) / 2)
#        display.text(line, x_offset, y, WIDTH, scale = 3, spacing = 3)
        x_text, y_text, w_text, h_text = vector.measure_text(line)
        x_offset = int((WIDTH - w_text) / 2)
        vector.text(line, x_offset, y)
        y += line_space
    
    utc_plus_button.draw()
    utc_minus_button.draw()

    presto.update()

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)

vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

vector.set_font("Roboto-Medium.af", 96)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)

# Clear the screen before the network call is made
display.set_pen(BLACK)
display.clear()
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
    ntp_time_set = time.time()
except OSError:
    while True:
        show_message("Unable to get time.\n\nCheck your network try again.")

utc_plus_button = button(display, vector, 'UTC +', WHITE, BLACK,  WIDTH - (WIDTH // 4), HEIGHT - 30, WIDTH // 4, 30, 5)
utc_minus_button = button(display, vector, 'UTC -', WHITE, BLACK, 0, HEIGHT - 30, WIDTH // 4, 30, 5)

# Offset of zero, no daylight saving or region
UTC_OFFSET = 0

while True:
    # Get a time checkpoint for multiple uses below
    time_check = time.time()
    
    # Update the RTC once a day
    if time_check - ntp_time_set > 60 * 60 * 24:
        try:
            ntptime.settime()
            ntp_time_set = time.time()
        except OSError:
            # Report and carry on, RTC is probably going to be close to right for a long time
            print("Unable to contact NTP server")

    # Update the screen
    time_phrase = update()
    draw(time_phrase)

    # 30 second tight loop to be responsive to button presses
    while time_check + 30 >= time.time():
        presto.touch.poll()
        update_needed = False
        if utc_plus_button.pressed():
            while utc_plus_button.pressed():
                presto.touch.poll()
            UTC_OFFSET += 1
            update_needed = True
        if utc_minus_button.pressed():
            while utc_minus_button.pressed():
                presto.touch.poll()
            UTC_OFFSET -= 1
            update_needed = True
        # Redraw the screen if needed
        if update_needed:
            time_phrase = update()
            draw(time_phrase)