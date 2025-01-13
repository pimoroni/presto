# Presto

Most of your interaction with Presto will be through the `presto` module.

It will help you set up PicoGraphics, touch, WiFi, ambient lighting and more.

## Getting Started

Create a new Presto instance:

```python
from presto import Presto

presto = Presto()
```

The `Presto()` class accepts some optional arguments:

* `full_res=True/False` - Use 480x480 resolution (slower but crisp!)
* `ambient_light=True/False` - automatically run the onboard LEDs
* `layers=1/2` - optionally use multiple layers in PicoGraphics
* `direct_to_fb=True/False` - in `full_res` mode, draws directly to the front-buffer

## Features

### Updating The Display

Presto provides you a PicoGraphics instance at `presto.display`, we usually
alias this in code like so:

```python
display = presto.display
```

Once you've done your normal PicoGraphics/PicoVector drawing operations you
can either:

* `presto.update()` - Copy the full front-buffer to the back buffer
* `presto.partial_update(x, y, w, h)` - Copy part of the front-buffer to the back buffer

### Touch

Presto ostensibly supports two simultaneous touches, but there are some caveats.

Touches that line up horizontally - such as a two finger vertical scroll - will
not be correctly registered. This is a known issue with the touch feature and
not a problem with your board!

Touches one above the other - two separate horizontal sliders, or maybe a friendly
game of pong? - should register fine!

To access touch information you can use:

* `presto.touch_a` - (Property) a three tuple of X, Y and state (True for touched)
* `presto.touch_b` - (Property) a three tuple of X, Y and state
* `presto.touch_delta` - (Property) a two tuple of distance and angle between touches
* `presto.touch_poll()` - Force the touch to be updated

### Back/Ambient Lights

If you've set `ambient_light=True` then Presto will automatically update the LEDs
to match the screen content.

Note - you can disable this with `presto.auto_ambient_leds(False)`.

Otherwise you can use either MicroPython's `neopixel` library or our `Plasma` to
drive the LEDs.

#### Using the NeoPixel Library

```python
import neopixel

NUM_LEDS = 7
LED_PIN = 33

lights = neopixel.NeoPixel(machine.Pin(LED_PIN), NUM_LEDS)

lights[0] = (255, 255, 0)

lights.write()
```

#### Using the Plasma Library


```python
import plasma

NUM_LEDS = 7
LED_PIN = 33

lights = plasma.WS2812(NUM_LEDS, 0, 0, LED_PIN)
lights.start()

lights.set_hsv(0, 0.5, 1.0, 1.0)
lights.set_rgb(1, 255, 255, 0)
```

### Wireless

Presto assumes you have a `secrets.py` with the format:

```python
WIFI_SSID = "Your SSID"
WIFI_PASSWORD = "Password"
```

Then you can simply:

```python
connection_successful = presto.connect()
```

For tips on reporting connection status on-screen [see the wifi docs](wifi.md).
