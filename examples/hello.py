from presto import Presto

# Setup for the Presto display
presto = Presto(reactive_backlight=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Couple of colours for use later
BLUE = display.create_pen(28, 181, 202)
WHITE = display.create_pen(255, 255, 255)


while True:

    # Clear the screen and use blue as the background colour
    display.set_pen(BLUE)
    display.clear()
    # Set the pen to a different colour otherwise we won't be able to see the text!
    display.set_pen(WHITE)

    # draw the text
    display.text("Hello!", 10, 85, WIDTH, 8)

    # Finally we update the screen with our changes :)
    presto.update()
