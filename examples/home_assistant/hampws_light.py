from config import HA_HOST, HA_TOKEN, LIGHT_ENTITIES
from hampws import HAMPWS
from presto import Presto
from touch import Button

# Initialize Presto
presto = Presto()
display = presto.display
touch = presto.touch
WIDTH, HEIGHT = display.get_bounds()

# Define colors
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
YELLOW = display.create_pen(255, 255, 0)

# Create button
button = Button(10, 35, 100, 50)

# Initialize Home Assistant connection
ws = HAMPWS(HA_HOST, HA_TOKEN)
if not ws.connect():
    raise Exception("Failed to connect to Home Assistant")

# Get the first light entity
first_light = list(LIGHT_ENTITIES.values())[0]['entity_id']

def get_light_state():
    """Get the current state of the light"""
    state = ws.get_state(first_light)
    print(f"Raw state data: {state}")  # Debug output
    if state:
        state_value = state.get('state', '').lower()
        print(f"State value: {state_value}")  # Debug output
        return state_value == 'on'
    return False

def toggle_light(current_state):
    """Toggle the light state"""
    service = "turn_off" if current_state else "turn_on"
    ws.call_service("light", service, 
                   target={"entity_id": first_light})

try:
    # Subscribe to state changes
    print("Subscribing to state changes...")
    sub_id = ws.subscribe_events("state_changed")
    if not sub_id:
        print("Warning: Failed to subscribe to state changes. Continuing without state updates.")
    
    # Initial light state
    print(f"\nGetting initial light state...")  # Debug output
    light_state = get_light_state()
    print(f"Initial light state parsed as: {'ON' if light_state else 'OFF'}")
    
    # Touch tracking
    was_pressed = False
    
    while True:
        # Handle touch first
        touch.poll()
        
        # Check if button is currently pressed
        is_pressed = touch.state and button.is_pressed()
        
        # Only toggle on new presses
        if is_pressed and not was_pressed:
            toggle_light(light_state)
            light_state = not light_state  # Immediately update display state
            print(f"Light toggled to: {'ON' if light_state else 'OFF'}")
        
        # Update previous state
        was_pressed = is_pressed
        
        # Clear display
        display.set_pen(WHITE)
        display.clear()
        
        # Draw button with current state color
        display.set_pen(YELLOW if light_state else BLACK)
        display.rectangle(*button.bounds)
        
        # Draw text
        display.set_pen(BLACK)
        display.text("Light Control", 10, 10, scale=2)
        state_text = "ON" if light_state else "OFF"
        display.text(state_text, button.x + 35, button.y + 15, scale=2)
        
        # Update display
        presto.update()
        
        # Check for state changes
        if sub_id:
            message = ws.read_message()
            if message and message.get('type') == 'event' and \
               message.get('event', {}).get('event_type') == 'state_changed':
                data = message['event']['data']
                entity_id = data.get('entity_id', '')
                if entity_id == first_light:
                    new_state = data.get('new_state', {}).get('state', '')
                    light_state = (new_state.lower() == 'on')
                    print(f"Light state changed to: {'ON' if light_state else 'OFF'}")

except KeyboardInterrupt:
    print("\nProgram stopped by user")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    ws.close()
