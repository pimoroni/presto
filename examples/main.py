import time
import math
import os
import machine
import psram
import plasma

from presto import Presto
from picovector import ANTIALIAS_FAST, PicoVector, Polygon, Transform, HALIGN_CENTER

psram.mkramfs()

try:
    os.stat("/ramfs/launch.txt")[0] & 0x4000 == 0
    f = open("/ramfs/launch.txt", "r")
    result = f.readline()
    f.close()
except OSError:
    result = False

if result and result.endswith(".py"):
    os.remove("/ramfs/launch.txt")
    __import__(result[:-3])

bl = plasma.WS2812(7, 0, 0, 33)
bl.start()

# Setup for the Presto display
presto = Presto(ambient_light=False)

display = presto.display
WIDTH, HEIGHT = display.get_bounds()
CY = HEIGHT // 2
CX = WIDTH // 2

OFFSET_X = 0
OFFSET_Y = -30

RADIUS_X = 160
RADIUS_Y = 30

# Couple of colours for use later
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
BACKGROUND = display.create_pen(255, 250, 240)

# We do a clear and update here to stop the screen showing whatever is in the buffer.
display.set_pen(BLACK)
display.clear()
presto.update()

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_FAST)
vector.set_font("Roboto-Medium.af", 10)
vector.set_font_align(HALIGN_CENTER)
t = Transform()


class Application:
    DEFAULT_ICON = [
        [(-10.0, 12.5), (10.0, 12.5), (10.0, 7.5), (-10.0, 7.5), (-10.0, 12.5)],
        [(-10.0, 2.5), (10.0, 2.5), (10.0, -2.5), (-10.0, -2.5), (-10.0, 2.5)],
        [
            (-15.0, 22.5),
            (-16.43, 22.31),
            (-17.75, 21.71),
            (-18.52, 21.11),
            (-19.47, 19.78),
            (-19.92, 18.46),
            (-20.0, 17.56),
            (-20.0, -22.5),
            (-19.77, -24.05),
            (-18.82, -25.73),
            (-17.79, -26.64),
            (-16.69, -27.21),
            (-15.06, -27.5),
            (5.0, -27.5),
            (20.0, -12.5),
            (20.0, 17.5),
            (19.77, 19.04),
            (19.36, 19.95),
            (18.55, 21.02),
            (17.74, 21.68),
            (16.7, 22.21),
            (15.06, 22.5),
            (-15.0, 22.5),
        ],
        [
            (2.5, -10.0),
            (2.5, -22.5),
            (-15.0, -22.5),
            (-15.0, 17.5),
            (15.0, 17.5),
            (15.0, -10.0),
            (2.5, -10.0),
        ]
    ]

    maximum_scale = 1.6
    minimum_scale = 0.6

    def __init__(self, w, h, file):
        global icon_count
        self.index = icon_count
        icon_count += 1

        self.selected = False
        self.icon = Polygon()
        self.name = file[:-3]
        self.description = ""

        with open(file) as f:
            header = [f.readline().strip() for _ in range(3)]

        for line in header:
            if line.startswith("# ICON "):
                try:
                    for path in eval(line[7:]):
                        self.icon.path(*path)
                except:  # noqa: E722 - eval could barf up all kinds of nonsense
                    pass
            else:
                # If there's no icon in the file header we'll use the default.
                for path in self.DEFAULT_ICON:
                    self.icon.path(*path)

            if line.startswith("# NAME "):
                self.name = line[7:]
            if line.startswith("# DESC "):
                self.description = line[7:]

        self.w = w
        self.h = h
        self.file = file

        # Background
        self.i = Polygon()
        self.i.rectangle(0 - w / 2, 0 - h / 2, w, h, (10, 10, 10, 10))

        # Outline
        self.ol = Polygon()
        self.ol.rectangle(0 - w / 2, 0 - h / 2, w, h, (10, 10, 10, 10), stroke=2)

        # Transform
        self.t = Transform()

        self.angle = 0
        self.scale = 0
        self.x = 0
        self.y = 0

        self.color_fg = None
        self.color_bg = None
        self.color_ol = None

    def __lt__(self, icon):
        return self.scale < icon.scale

    def touched(self, touch):
        x, y, w, h = self.bounds()
        return touch.x > x and touch.x < x + w and touch.y > y and touch.y < y + h

    def update(self, move_angle):
        angle_per_icon = 2 * math.pi / icon_count
        self.angle = angle_per_icon * self.index + move_angle

        self.angle %= 2 * math.pi

        scale_factor = (math.cos(self.angle) + 1.0) / 2
        self.scale = max(self.minimum_scale, scale_factor) * self.maximum_scale

        # The lower the lower bounds here, the less saturated
        s = min(0.6, scale_factor + 0.1)

        self.hue = (angle_per_icon * self.index) / (2 * math.pi)
        self.color_fg = display.create_pen_hsv(self.hue, s, 0.2)
        self.color_ol = display.create_pen_hsv(self.hue, s, 1.0)
        self.color_bg = display.create_pen_hsv(self.hue, s, 0.9)

        self.y = RADIUS_Y * math.cos(self.angle)
        self.x = RADIUS_X * math.sin(self.angle)

        # Quick and dirty way to "perspective correct" the circle
        self.x *= self.scale

        # Logically these things below happen in reverse order
        # but because these are matrix operations we need to apply them back to front
        # THIS IS WEIRD BUT MATHS GON' MATHS
        self.t.reset()
        # Translate to our final display offset
        self.t.translate(OFFSET_X, OFFSET_Y)
        # Translate back to screen space, moving origin 0, 0 to our X and Y
        self.t.translate(CX + self.x, CY + self.y)
        # Scale the icon around origin 0, 0
        self.t.scale(self.scale, self.scale)

    def draw(self, selected=False):
        # Bit of formatting for scripts without a title in the header.
        name = self.name.replace("_", " ")
        name = " ".join([w[0].upper() + w[1:] for w in name.split()])

        display.set_pen(self.color_bg)
        vector.set_transform(self.t)
        vector.draw(self.i)
        display.set_pen(self.color_fg)
        self.t.translate(0, 2)
        vector.draw(self.icon)

        if selected:
            self.t.translate(0, -2)
            display.set_pen(BLACK)
            vector.set_font_size(10)
            vector.text(name, -self.w // 2, 40, max_width=self.w)
            display.set_pen(self.color_ol)
            vector.draw(self.ol)
            vector.set_font_size(8)
            desc_length = vector.measure_text(self.description, 18)
            vector.text(
                self.description,
                -int(desc_length[2]) // 2,
                50,
                max_width=int(desc_length[2]) + 5,
            )

        # Useful for debugging
        # display.rectangle(*self.bounds())

    def bounds(self):
        w = self.w * self.scale
        h = self.h * self.scale
        x = -w // 2
        y = -h // 2

        return (
            int(x + self.x + CX + OFFSET_X),
            int(y + self.y + CY + OFFSET_Y),
            int(w),
            int(h),
        )

    def launch(self):
        with open("/ramfs/launch.txt", "w") as f:
            f.write(self.file)

        # Clear the display buffer before launching the next app
        display.set_pen(BLACK)
        display.clear()
        presto.update()

        # Reset!
        machine.reset()


icon_count = 0


files = [
    file
    for file in os.listdir()
    if file.endswith(".py") and file not in ("main.py", "secrets.py")
]
w = 60
h = 60
icons = [Application(w, h, x) for x in files]

num_icons = len(icons)

sx, sy = 0, 0
ex, ey = 0, 0
st, et = None, None
touch_ms = 0
touch_dist = 0
touch_speed = 0
touch_dir = 0
tap = False

move_angle = 0
move = 0
friction = 0.98

bg = Polygon()
bg.rectangle(0, 0, WIDTH, HEIGHT, (10, 10, 10, 10))

while True:
    # Take a local reference to touch for a tiny performance boost
    touch = presto.touch

    vector.set_transform(t)
    t.reset()

    display.set_pen(BLACK)
    display.clear()
    display.set_pen(BACKGROUND)

    vector.draw(bg)

    touch.poll()

    if touch.state and st is None:
        st = time.ticks_ms()
        sx, sy = touch.x, touch.y
        tap = True

    elif touch.state:
        ex, ey = touch.x, touch.y

        et = time.ticks_ms()
        touch_ms = et - st  # et phone home
        # get the x distance between the touch start and current touch
        touch_dist = abs(sx - ex)
        # Get the touch direction bounded to -1, 0, +1, for easy multiply later
        touch_dir = max(min(1, sx - ex), -1)
        # Calculate the touch speed, speed = distance / time
        touch_speed = touch_dist / touch_ms
        touch_speed *= 2

        # Any movement at all should cancel our tap action
        if touch_dist > 4:
            tap = False

        # If a touch is under this minimal distance it counts as a "stop spinning, darn it"
        if touch_dist > 10:
            # Apply the touch speed with the direction multiplier from above
            move -= math.radians(touch_speed * touch_dir)
            if touch_speed > 1:
                friction = 0.98  # Normal friction ( the closer this is to 1 the longer it will take to slow down )
            else:
                friction = 0.8
        else:
            # Pick the one you like best
            # move = 0      # Stop abruptly
            friction = 0.7  # Apply a braking friction
    else:
        st = None

    move_angle += move         # Apply the movement distance, this is in degrees and needs finagled to follow your finger
    move_angle %= 2 * math.pi  # Wrap to 0-359
    move *= friction           # Apply friction, this will slowly decrease "move" when there's no touch, to slow the spin down

    # Pre-calculate the scales and angles
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
        bl.set_hsv(i, hue, 1.0, 0.5)

    presto.update()
