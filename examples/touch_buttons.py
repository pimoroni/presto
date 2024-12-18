from presto import Presto
from touch import Button

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Couple of colours for use later
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
GREEN = display.create_pen(9, 185, 120)
BLACK = display.create_pen(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

CX = WIDTH // 2
CY = HEIGHT // 2
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# Create a touch button and set the touch region.
# Button(x, y, width, height)
button_1 = Button(10, 35, BUTTON_WIDTH, BUTTON_HEIGHT)
button_2 = Button(10, 95, BUTTON_WIDTH, BUTTON_HEIGHT)
button_3 = Button(10, 155, BUTTON_WIDTH, BUTTON_HEIGHT)

while True:

    # Check for touch changes
    touch.poll()

    # Clear the screen and set the background colour
    display.set_pen(WHITE)
    display.clear()
    display.set_pen(BLACK)

    # Title text
    display.text("Touch Button Demo", 23, 7)

    # Finding the state of a touch button is much the same as a physical button
    # calling '.is_pressed()' on your button object will return True or False
    if button_1.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 1!", (button_1.x + button_1.w) + 20, button_1.y + 3, 100, 2)
    else:
        display.set_pen(RED)

    # We've defined our touch Button object but we need a visual representation of it for the user!
    # We can use the '.bounds' property of our Button object to set the X, Y, WIDTH and HEIGHT
    display.rectangle(*button_1.bounds)

    if button_2.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 2!", (button_2.x + button_2.w) + 20, button_2.y + 3, 100, 2)
    else:
        display.set_pen(RED)

    display.rectangle(*button_2.bounds)

    if button_3.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 3!", (button_3.x + button_3.w) + 20, button_3.y + 3, 100, 2)
    else:
        display.set_pen(RED)

    display.rectangle(*button_3.bounds)

    # Finally, we update the screen so we can see our changes!
    presto.update()
