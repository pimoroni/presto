from picovector import color, font, shape
from presto import Buzzer, Presto
from touch import Button

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height

# CONSTANTS
CX = WIDTH // 2
CY = HEIGHT // 2

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 110

display.font = font.load("Roboto-Medium.af")

# Couple of colours for use later
WHITE = color.rgb(255, 255, 255)
RED = color.rgb(230, 60, 45)
BLACK = color.rgb(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

# Define our button vectors and touch button
button = Button(CX - (BUTTON_WIDTH // 2), CY - (BUTTON_HEIGHT // 2), BUTTON_WIDTH, BUTTON_HEIGHT)
button_vector = shape.circle(CX, CY, 50)
button_outline = shape.circle(CX, CY, 54).stroke(5)

# Calculate our text positions now rather than in the main loop
TEXT_SIZE = 28
w, h = display.measure_text("TOUCH", TEXT_SIZE)
text_x = int(CX - (w // 2))
text_y = int(CY - (h // 2))
text_x_offset = text_x + 2
text_y_offset = text_y + 2

# Setup the buzzer. The Presto piezo is on pin 43.
buzzer = Buzzer(43)

while True:

    # Check for touch changes
    touch.poll()

    # Clear the screen and set the background colour
    display.pen = WHITE
    display.clear()

    # Draw the touch button outline and inner section
    display.pen = BLACK
    display.shape(button_outline)
    display.pen = RED
    display.shape(button_vector)

    # Draw vector text with drop shadow
    display.pen = BLACK
    display.text("TOUCH", text_x_offset, text_y_offset, TEXT_SIZE)
    display.pen = WHITE
    display.text("TOUCH", text_x, text_y, TEXT_SIZE)

    # If we're pressing the onscreen button, play a tone!
    # otherwise play nothing :)
    if button.is_pressed():
        buzzer.set_tone(150)
    else:
        buzzer.set_tone(-1)

    # Finally, we update the screen so we can see our changes!
    presto.update()
