import time
import machine
import ntptime
import pngdec
from presto import Presto

# --------------------------
# CHOOSE YOUR UTC OFFSET IN HOURS
# E.g. New York is -5 (EST), -4 (EDT)
OFFSET_HOURS = -5 #EST
# --------------------------

# How often (in minutes) to check NTP
NTP_SYNC_INTERVAL = 10  # try to sync every 10 minutes

# --------------------------
# DIGITAL CLOCK OPTION
# Off by default, helps with debugging
SHOW_DIGITAL_CLOCK = False
# --------------------------

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Global references
rtc = machine.RTC()
time_string = None

# List of all "words" in your background layout.
words = [
    "it", "d", "is", "m", "about", "lv", "half", "c", "quarter", "b",
    "to", "past", "n", "one", "two", "three", "four", "five", "six",
    "eleven", "ten", "d", "qdh", "eight", "seven", "rm", "twelve",
    "nine", "p", "ncsnheypresto", "O'Clock", "agrdsp"
]

# Connect to Wi-Fi (if your Presto is the wireless variant).
wifi = presto.connect()

# Attempt initial time sync from NTP (RTC = UTC) at startup
try:
    ntptime.settime()
    last_ntp_sync = time.time()  # record when we synced
except OSError:
    print("Unable to contact NTP server")
    last_ntp_sync = 0  # if it fails, we'll try again soon

# Define some pen colors
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
GRAY  = display.create_pen(120, 120, 120)

def approx_time(hours, minutes):
    """
    Convert numeric hours/minutes into a phrase like:
    "it is about quarter past three"

    'hours' should be in 12-hour format (1..12).
    """
    nums = {
        0:  "twelve", 
        1:  "one", 
        2:  "two", 
        3:  "three",
        4:  "four", 
        5:  "five", 
        6:  "six", 
        7:  "seven",
        8:  "eight", 
        9:  "nine", 
        10: "ten", 
        11: "eleven",
        12: "twelve"
    }

    if 0 <= minutes < 8:
        return "it is about " + nums[hours] + " O'Clock"
    elif 8 <= minutes < 23:
        return "it is about quarter past " + nums[hours]
    elif 23 <= minutes < 38:
        return "it is about half past " + nums[hours]
    elif 38 <= minutes < 53:
        return "it is about quarter to " + nums[(hours % 12) + 1]
    else:
        return "it is about " + nums[(hours % 12) + 1] + " O'Clock"


def update():
    """
    Builds the approximate phrase ("quarter to nine") 
    using the *current* local time in the RTC 
    (we no longer call ntptime.settime() here).
    """
    global time_string

    # The RTC is in UTC. Convert to local time with OFFSET_HOURS.
    local_seconds = time.time() + (OFFSET_HOURS * 3600)
    current_t = time.localtime(local_seconds)

    # Convert from 24-hour (0..23) to 12-hour (1..12).
    hour_24 = current_t[3]
    minute  = current_t[4]

    hour_12 = hour_24 % 12
    if hour_12 == 0:
        hour_12 = 12

    # Create the "it is about quarter to nine" style phrase
    phrase = approx_time(hour_12, minute)

    # Split into separate words for highlighting
    time_string = phrase.split()

    print("Approx phrase:", time_string)


def draw():
    """
    Draws the background, the word-clock highlight,
    then also draws a numeric HH:MM time at the bottom,
    centered, in gray, using letter-by-letter spacing.
    """
    global time_string

    display.set_font("bitmap8")
    display.set_layer(1)  # Foreground layer

    # Clear screen to black
    display.set_pen(BLACK)
    display.clear()

    # Spacing variables used across both word clock & digital time
    default_x    = 25
    x            = default_x
    y            = 35
    line_space   = 20
    letter_space = 15
    margin       = 25
    scale        = 1
    spacing      = 1

    #
    # Draw the "word clock" words
    #
    for word in words:
        if word in time_string:
            display.set_pen(WHITE)  # highlight
        else:
            display.set_pen(GRAY)   # dim

        for letter in word:
            text_length = display.measure_text(letter, scale, spacing)
            if (x + text_length) > (WIDTH - margin):
                y += line_space
                x = default_x

            display.text(letter.upper(), x, y, WIDTH, scale=scale, spacing=spacing)
            x += letter_space

    #
    # Optionally draw numeric HH:MM at the bottom, centered, in gray,
    # with letter-by-letter spacing.
    #
    if SHOW_DIGITAL_CLOCK:
        local_seconds = time.time() + (OFFSET_HOURS * 3600)
        current_t = time.localtime(local_seconds)
        hour_24 = current_t[3]
        minute  = current_t[4]

        numeric_time_str = "{:02d}:{:02d}".format(hour_24, minute)

        # Measure total width of all characters + spacing
        total_width = 0
        for i, letter in enumerate(numeric_time_str):
            char_width = display.measure_text(letter, scale, spacing)
            total_width += char_width
            if i < len(numeric_time_str) - 1:
                total_width += letter_space

        # Calculate starting x so the string is centered
        x_time = (WIDTH - total_width) // 2
        y_time = HEIGHT - 20  # 20 px up from bottom (adjust as desired)

        # Use GRAY pen for the digital time
        display.set_pen(GRAY)

        # Draw each character with letter spacing
        for i, letter in enumerate(numeric_time_str):
            char_width = display.measure_text(letter, scale, spacing)

            display.text(letter.upper(), x_time, y_time, WIDTH, scale=scale, spacing=spacing)

        # Advance x_time
            x_time += char_width
            if i < len(numeric_time_str) - 1:
                x_time += letter_space

    # Finally, push changes to the display
    presto.update()


# ------------------------------------------------------
# Set the background in layer 0 (behind the words)
# ------------------------------------------------------
display.set_layer(0)
try:
    p = pngdec.PNG(display)
    p.open_file("wordclock_background.png")
    p.decode(0, 0)
except OSError:
    # If background image isn't found, just clear
    display.set_pen(BLACK)
    display.clear()

# --------------------------------
# Main loop
# --------------------------------
while True:
    # 1) Check if it's time to sync with NTP again (every 10 minutes)
    now = time.time()
    sync_age = now - last_ntp_sync
    if sync_age >= (NTP_SYNC_INTERVAL * 60):
        try:
            ntptime.settime()
            last_ntp_sync = now
            print("NTP sync successful.")
        except OSError:
            print("Unable to contact NTP server")

    # 2) Update approximate phrase & draw display
    update()
    draw()

    # 3) Sleep 1 minute before next refresh
    time.sleep(60)
