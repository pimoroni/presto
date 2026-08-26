import math
import os
import time

import machine
import psram
from picovector import brush, color, font, image, mat3, shape, vec2
from presto import Presto

psram.mkramfs()

try:
    with open("/ramfs/launch.txt", "r") as f:
        result = f.readline()
except OSError:
    result = ""

if result.endswith(".py"):
    os.remove("/ramfs/launch.txt")
    __import__(result[:-3])

# Setup for the Presto display
presto = Presto(ambient_light=False)

display = presto.display

WIDTH, HEIGHT = display.width, display.height

icons = {
    "travel": "\ue6ca",
    "bomb": "\uf568",
    "lightbulb": "\ue0f0",
    "deployed-code": "\uf720",
    "photo-library": "\ue413",
    "joystick": "\uf5ee",
    "monitoring": "\uf190",
    "timer": "\ue425",
    "description": "\ue873",
    "schedule": "\ue8b5"
}

CENTER_Y = HEIGHT // 2
CENTER_X = WIDTH // 2

OFFSET_X = 0
OFFSET_Y = -30

RADIUS_X = 160
RADIUS_Y = 30

# Couple of colours for use later
BLACK = color.rgb(0, 0, 0)

# clear() takes a brush, which costs about a fifth of a millisecond more than
# filling flat. Drawing a full screen rectangle instead would double the frame.
# Travelling further across the colour space also narrows the RGB565 banding:
# these stops step every 1.7 pixels where a subtler pair banded every 3.
BACKDROP = brush.gradient(
    brush.LINEAR, 0, 0, 0, HEIGHT,
    [(0.0, color.rgb(255, 247, 235)), (1.0, color.rgb(150, 176, 214))],
)

# Once a fling has died down, ease the front-most icon onto centre rather than
# leaving it parked between two.
SNAP_ENGAGE = 0.02
SNAP_EASE = 0.2

# We do a clear and update here to stop the screen showing whatever is in the buffer.
display.pen = BLACK
display.clear()
presto.update()

display.font = font.load("Roboto-Medium-With-Material-Symbols.af")
display.antialias = image.X4


def rounded_contour(x, y, w, h, r, steps=6):
    # A rounded rectangle as a point list, so it can be the inner contour of the
    # corner mask. shape.rounded_rectangle can't be combined with another path.
    points = []
    for cx, cy, start in ((x + w - r, y + h - r, 0), (x + r, y + h - r, 90),
                          (x + r, y + r, 180), (x + w - r, y + r, 270)):
        for step in range(steps + 1):
            a = math.radians(start + 90 * step / steps)
            points.append(vec2(cx + r * math.cos(a), cy + r * math.sin(a)))
    return points


def text_centered(text, cx, baseline, size):
    # text() hangs from the top of the em box; these were positioned by baseline.
    display.text(text, cx - display.measure_text(text, size)[0] / 2, baseline - size, size)


def icon_centered(glyph, cx, cy, size):
    # The Material Symbols glyphs are drawn centred on x and render about twice
    # the nominal size, so they need centring on their ink rather than on the
    # advance width the way the Latin text above does.
    display.text(glyph, cx, cy - size, size)


# Touch tracking and menu movement
touch_start_x = 0
touch_start_time = None
tap = False

move_angle = 0
move = 0
friction = 0.98

# Rounded corners: everything outside the rounded rectangle, filled black.
rounded_corners = shape.custom(
    [vec2(0, 0), vec2(WIDTH, 0), vec2(WIDTH, HEIGHT), vec2(0, HEIGHT)],
    rounded_contour(0, 0, WIDTH, HEIGHT, 10),
)


class Application:
    maximum_scale = 1.6
    minimum_scale = 0.6
    count = 0

    def __init__(self, w, h, file):
        self.index = Application.count
        Application.count += 1

        self.selected = False
        self.icon = icons["description"]

        # Bit of filename formatting for scripts without a title in the header.
        self.name = " ".join([w[0].upper() + w[1:] for w in file[:-3].replace("_", " ").split()])
        self.description = ""

        with open(file) as f:
            header = [f.readline().strip() for _ in range(3)]

        for line in header:
            if line.startswith("# ICON "):
                icon = line[7:].strip()
                # ignore any icon not in the approved list
                # this includes older co-ordinate based icons, often found in sample code
                if icon in icons:
                    self.icon = icons[icon]

            if line.startswith("# NAME "):
                self.name = line[7:]

            if line.startswith("# DESC "):
                self.description = line[7:]

        self.w = w
        self.h = h
        self.file = file

        # Background and outline, drawn around the origin so the transform can
        # place and scale them.
        self.bg = shape.rounded_rectangle(0 - w / 2, 0 - h / 2, w, h, 10)
        self.ol = shape.rounded_rectangle(0 - w / 2, 0 - h / 2, w, h, 10).stroke(2)

        self.angle = 0
        self.scale = 0
        self.x = 0
        self.y = 0

        self.color_fg = None
        self.color_bg = None
        self.color_ol = None
        self.brush_bg = None

    def __lt__(self, icon):
        return self.scale < icon.scale

    def touched(self, touch):
        x, y, w, h = self.bounds()
        return touch.x > x and touch.x < x + w and touch.y > y and touch.y < y + h

    def update(self, move_angle):
        angle_per_icon = 2 * math.pi / Application.count
        self.angle = angle_per_icon * self.index + move_angle

        self.angle %= 2 * math.pi

        scale_factor = (math.cos(self.angle) + 1.0) / 2
        self.scale = max(self.minimum_scale, scale_factor) * self.maximum_scale

        # The lower the lower bounds here, the less saturated
        s = min(0.6, scale_factor + 0.1)

        self.hue = (angle_per_icon * self.index) / (2 * math.pi)
        hue_deg = self.hue * 360
        saturation = int(s * 255)
        self.color_fg = color.hsv(hue_deg, saturation, int(0.2 * 255))
        self.color_ol = color.hsv(hue_deg, saturation, 255)
        self.color_bg = color.hsv(hue_deg, saturation, int(0.9 * 255))

        # Gradient stops are in the shape's own space, so this follows the tile
        # transform without being rebuilt for the tile's position or scale.
        self.brush_bg = brush.gradient(
            brush.LINEAR, 0, -self.h / 2, 0, self.h / 2,
            [(0.0, color.hsv(hue_deg, max(0, saturation - 40), 255)),
             (1.0, color.hsv(hue_deg, saturation, int(0.7 * 255)))],
        )

        self.y = RADIUS_Y * math.cos(self.angle)
        self.x = RADIUS_X * math.sin(self.angle)

        # Quick and dirty way to "perspective correct" the circle
        self.x *= self.scale

        # Screen position of this icon's centre.
        self.screen_x = CENTER_X + self.x + OFFSET_X
        self.screen_y = CENTER_Y + self.y + OFFSET_Y

        # Logically these things below happen in reverse order
        # but because these are matrix operations we need to apply them back to front
        # THIS IS WEIRD BUT MATHS GON' MATHS
        transform = mat3()
        # Translate to our final display offset
        transform.translate(OFFSET_X, OFFSET_Y)
        # Translate back to screen space, moving origin 0, 0 to our X and Y
        transform.translate(CENTER_X + self.x, CENTER_Y + self.y)
        # Scale the icon around origin 0, 0
        transform.scale(self.scale, self.scale)

        self.bg.transform = transform
        self.ol.transform = transform

    def draw(self, selected=False):
        # The icon and its labels used to be drawn through the same matrix as
        # the tile, so their sizes scaled along with their positions.
        display.pen = self.brush_bg
        display.shape(self.bg)
        display.pen = self.color_fg
        icon_centered(self.icon, self.screen_x, self.screen_y, 20 * self.scale)

        if selected:
            display.pen = BLACK
            text_centered(self.name, self.screen_x, self.screen_y + 40 * self.scale, 10 * self.scale)
            display.pen = self.color_ol
            display.shape(self.ol)
            text_centered(self.description, self.screen_x, self.screen_y + 50 * self.scale, 8 * self.scale)

        # Useful for debugging
        # display.rectangle(*self.bounds())

    def bounds(self):
        w = self.w * self.scale
        h = self.h * self.scale

        return (
            int(self.screen_x - w // 2),
            int(self.screen_y - h // 2),
            int(w),
            int(h),
        )

    def launch(self):
        with open("/ramfs/launch.txt", "w") as f:
            f.write(self.file)

        # Clear the display buffer before launching the next app
        display.pen = BLACK
        display.clear()
        presto.update()

        # Reset!
        machine.reset()


icons = [
    Application(60, 60, file) for file in os.listdir()
    if file.endswith(".py") and file not in ("main.py", "secrets.py")]

# Take a local reference to touch for a tiny performance boost
touch = presto.touch

while True:
    # Clear screen to our background gradient
    display.pen = BACKDROP
    display.clear()

    # Draw rounded corners in black
    display.pen = BLACK
    display.shape(rounded_corners)

    touch.poll()

    if touch.state and touch_start_time is None:
        touch_start_time = time.ticks_ms()
        touch_start_x = touch.x
        last_touch_x = touch.x
        tap = True

    elif touch.state:
        # Get the duration of the touch in milliseconds
        touch_ms = time.ticks_ms() - touch_start_time

        # Get the x distance between the touch start and current touch
        touch_dist = touch_start_x - touch.x

        # Calculate the touch speed, speed = distance / time
        touch_speed = touch_dist / touch_ms

        # Any movement should cancel our tap action
        if abs(touch_dist) > 4:
            tap = False

        # If a touch is under this minimal distance it counts as a "stop spinning, darn it"
        if abs(touch_dist) > 10:
            # Follow finger as it moves
            move = -math.radians(last_touch_x - touch.x) * 0.12
            last_touch_x = touch.x

            # Normal friction after touch ends ( the closer this is to 1 the longer it will take to slow down )
            friction = 0.8

        else:
            # Pick the one you like best
            # move = 0      # Stop abruptly
            friction = 0.7  # Apply a braking friction
    else:
        touch_start_time = None

    move_angle += move         # Apply the movement distance, this is in degrees and needs finagled to follow your finger
    move_angle %= 2 * math.pi  # Wrap at 360 degrees (in radians)
    move *= friction           # Apply friction, this will slowly decrease "move" when there's no touch, to slow the spin down

    # Settle onto the nearest icon once the user has let go and the spin has
    # slowed, so it stops parked half way between two.
    if touch_start_time is None and abs(move) < SNAP_ENGAGE:
        angle_per_icon = 2 * math.pi / Application.count
        target = round(move_angle / angle_per_icon) * angle_per_icon
        move_angle += (target - move_angle) * SNAP_EASE
        move_angle %= 2 * math.pi

    # Pre-calculate the scales and angles for sorting.
    for icon in icons:
        icon.update(move_angle)

    # We have implemented the __lt__ magic method on Icons so we can just sort them
    # by visual size- the biggest icon is at the front!
    sorted_icons = sorted(icons)

    # Draw all but the front-most icon
    for icon in sorted_icons[:-1]:
        icon.draw()

    # Draw the front-most selected icons, True == selected
    front_most_icon = sorted_icons[-1]
    front_most_icon.draw(True)

    if tap and not touch.state:
        tap = False
        if front_most_icon.touched(touch):
            front_most_icon.launch()

        # Handle touches on all the inactive icons
        for icon in sorted_icons[:-1]:
            if icon.touched(touch):
                a = icon.angle
                friction = 0.5  # The lower this value, the faster the transition
                if a - math.pi > 0:  # Take the shortest route
                    a = 2 * math.pi - a
                    move = a * (1.0 - friction)
                else:
                    move = -a * (1.0 - friction)

    # Cycle the hue of the backlight LEDs to match the icon colours
    hue = 1.0 - (move_angle % (2 * math.pi)) / (2 * math.pi)
    for i in range(7):
        presto.set_led_hsv(i, hue, 1.0, 0.5)

    presto.update()
