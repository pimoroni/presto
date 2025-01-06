from presto import Presto, Buzzer
from touch import Button
from picovector import ANTIALIAS_FAST, PicoVector, Polygon, Transform

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# CONSTANTS
CX = WIDTH // 2
CY = HEIGHT // 2

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 110

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_FAST)
t = Transform()

vector.set_font("Roboto-Medium.af", 54)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)

# Couple of colours for use later
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
BLACK = display.create_pen(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

# Define our button vectors and touch button
button = Button(CX - (BUTTON_WIDTH // 2), CY - (BUTTON_HEIGHT // 2), BUTTON_WIDTH, BUTTON_HEIGHT)
button_vector = Polygon()
button_vector.circle(CX, CY, 50)
button_outline = Polygon()
button_outline.circle(CX, CY, 54, 5)

# Calculate our text positions now rather than in the main loop
vector.set_font_size(28)
x, y, w, h = vector.measure_text("TOUCH", x=0, y=0, angle=None)
text_x = int(CX - (w // 2))
text_y = int(CY + (h // 2))
text_x_offset = text_x + 2
text_y_offset = text_y + 2

# Setup the buzzer. The Presto piezo is on pin 43.
buzzer = Buzzer(43)

while True:

    # Check for touch changes
    touch.poll()

    # Clear the screen and set the background colour
    display.set_pen(WHITE)
    display.clear()

    # Draw the touch button outline and inner section
    display.set_pen(BLACK)
    vector.draw(button_outline)
    display.set_pen(RED)
    vector.draw(button_vector)

    # Draw vector text with drop shadow
    display.set_pen(BLACK)
    vector.text("TOUCH", text_x_offset, text_y_offset)
    display.set_pen(WHITE)
    vector.text("TOUCH", text_x, text_y)

    # If we're pressing the onscreen button, play a tone!
    # otherwise play nothing :)
    if button.is_pressed():
        buzzer.set_tone(150)
    else:
        buzzer.set_tone(-1)

    # Finally, we update the screen so we can see our changes!
    presto.update()
