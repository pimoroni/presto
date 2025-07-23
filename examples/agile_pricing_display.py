# ICON [[(-20.0, 16.67), (-20.0, 12.22), (-15.56, 7.78), (-15.56, 16.67), (-20.0, 16.67)], [(-11.11, 16.67), (-11.11, 3.33), (-6.67, -1.11), (-6.67, 16.67), (-11.11, 16.67)], [(-2.22, 16.67), (-2.22, -1.11), (2.22, 3.39), (2.22, 16.67), (-2.22, 16.67)], [(6.67, 16.67), (6.67, 3.39), (11.11, -1.06), (11.11, 16.67), (6.67, 16.67)], [(15.56, 16.67), (15.56, -5.56), (20.0, -10.0), (20.0, 16.67), (15.56, 16.67)], [(-20.0, 5.17), (-20.0, -1.11), (-4.44, -16.67), (4.44, -7.78), (20.0, -23.33), (20.0, -17.06), (4.44, -1.5), (-4.44, -10.39), (-20.0, 5.17)]]
# NAME Energy Price
# DESC Shows last, current and next energy price.

"""
A demo for the Pimoroni Presto.
Shows the current, next and last energy price for Octopus Energys Agile Price tarrif
"""

import datetime
import time

import ntptime
import requests
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from presto import Presto

# Constants
# API_URL = 'https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-C/standard-unit-rates/'
API_URL = None  # Will try to guess the rates

# Find your region code: https://en.wikipedia.org/wiki/Meter_Point_Administration_Number#Distributor_ID
# This is required for automatic API endpoint detection
REGION_CODE = "_E"

# Print out API endpoints for debugging
DEBUG = True

# Setup for the Presto display

presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

t = Transform()
vector.set_font("Roboto-Medium.af", 54)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)

# Couple of colours for use later
ORANGE = display.create_pen(255, 99, 71)
ORANGE_2 = display.create_pen(255, 99 + 50, 71 + 50)
ORANGE_3 = display.create_pen(255, 99 + 20, 71 + 20)
ORANGE_4 = display.create_pen(255, 99 + 70, 71 + 70)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

MARGIN = 15


def show_message(text):
    display.set_pen(ORANGE)
    display.clear()
    display.set_pen(ORANGE_2)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


# Connect to the network and get time.
show_message("Connecting...")

try:
    presto.connect()
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
        show_message("Unable to get time.\n\nCheck network settings in 'secrets.py' and try again.")

# Keep a record of the last time we updated.
# We only want to be requesting new information every half an hour.
last_updated = time.time()


def get_api_endpoint():
    # Get the latest valid API endpoint for prices
    # First look up the right product in the products list
    request = requests.get("https://api.octopus.energy/v1/products/")
    json = request.json()
    product = [result for result in json["results"] if result["display_name"].startswith("Agile") and result["direction"] == "IMPORT" and result["brand"] == "OCTOPUS_ENERGY"][0]
    product_api_endpoint = [link["href"] for link in product["links"] if link["rel"] == "self"][0]

    # Now get the API endpoint URL by region code
    request = requests.get(product_api_endpoint)
    json = request.json()
    links = json["single_register_electricity_tariffs"][REGION_CODE]["direct_debit_monthly"]["links"]
    prices_api_endpoint = [link for link in links if link["rel"] == "standard_unit_rates"][0]["href"]

    if DEBUG:
        print(f"Got API endpoint: {prices_api_endpoint}")
    return prices_api_endpoint


def get_prices():
    try:
        # We only need the the first 6 elements covering the date and time
        t = time.localtime()[0:5]

        # Put that into a datetime object
        period_current = datetime.datetime(*t)
        period_next = period_current + datetime.timedelta(hours=1)
        period_last = period_current - datetime.timedelta(minutes=30)

        # Construct the time period to/from for our request later.
        request_string = (f"?period_from={period_last.year}-{period_last.month}-{period_last.day}T{period_last.hour}:{'00' if period_last.minute <= 29 else 30}Z"
                          f"&period_to={period_next.year}-{period_next.month}-{period_next.day}T{period_next.hour}:{'00' if period_next.minute <= 29 else '30'}Z")

        # Assemble our URL and make a request.
        request = requests.get(f"{API_URL}{request_string}")
        json = request.json()

        if DEBUG:
            print(f"Prices endpoint: {API_URL}{request_string}")

        # Finally we return our 3 values
        return json["results"][0]["value_inc_vat"], json["results"][1]["value_inc_vat"], json["results"][2]["value_inc_vat"]

    # if the above request fails, we want to handle the error and return values to keep the application running.
    except ValueError:
        return 0, 0, 0


# Get the correct API endpoint on start up, if it has not been specified already
if API_URL is None:
    API_URL = get_api_endpoint()

# Get the prices on start up, after this we'll only check again at the top of the hour.
next_price, current_price, last_price = get_prices()


while True:

    # Clear the screen and use orange as the background colour
    display.set_pen(ORANGE)
    display.clear()

    # Draw a big orange circle that's lighter than the background
    display.set_pen(ORANGE_4)
    v = Polygon()
    v.circle(0, HEIGHT // 2, 190)
    vector.draw(v)

    # Check if it has been over half an hour since the last update
    # if it has, update the prices again.
    if time.time() - last_updated > 1800:
        next_price, current_price, last_price = get_prices()
        last_updated = time.time()

    # Draw the drop shadows and the main text for the last, current and next prices.
    vector.set_font_size(28)
    display.set_pen(ORANGE_2)
    vector.text("last:", MARGIN, 50)
    vector.text(f"{last_price}p", MARGIN, 70)

    vector.set_font_size(52)

    display.set_pen(BLACK)
    vector.text("Now:", MARGIN + 2, 120 + 2)
    vector.set_font_size(58)
    vector.text(f"{current_price}p", MARGIN + 2, 160 + 2)

    display.set_pen(WHITE)
    vector.set_font_size(52)
    vector.text("Now:", MARGIN, 120)
    vector.set_font_size(58)
    vector.text(f"{current_price}p", MARGIN, 160)

    vector.set_font_size(28)
    display.set_pen(ORANGE_3)
    vector.text("Next:", MARGIN, 195)
    vector.text(f"{next_price}p", MARGIN, 215)

    # Finally we update the screen with our changes :)
    presto.update()
