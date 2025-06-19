from config import (
    HA_HOST, HA_TOKEN, 
    LIGHT_ENTITIES, SENSORS, CAMERAS
)
from hampws import HAMPWS
import time
import json

def test_paired_lights():
    """Test controlling paired back door lights"""
    print("\n=== Testing Paired Lights Control ===")
    ws = HAMPWS(HA_HOST, HA_TOKEN)
    
    if not ws.connect():
        print("Failed to connect")
        return
        
    try:
        # Get both light entities
        light_entities = [light['entity_id'] for light in LIGHT_ENTITIES.values()]
        
        msg_id = ws.message_id
        
        # Turn both lights on
        print(f"\nTurning on both back door lights...")
        ws._send_frame(json.dumps({
            "id": msg_id,
            "type": "call_service",
            "domain": "light",
            "service": "turn_on",
            "target": {"entity_id": light_entities},
            "service_data": {"brightness": 255}
        }))
        ws.message_id += 1
        
        # Wait for response and process state updates
        start_time = time.time()
        success = False
        while time.time() - start_time < 2:  # Wait up to 2 seconds
            message = ws.read_message()
            if message:
                print(f"Received message: {message}")
                if message.get('id') == msg_id:
                    success = message.get('success', False)
                    print("Turn on command Success!" if success else "Turn on command Failed!")
            time.sleep(0.1)
            
        msg_id = ws.message_id
        
        # Dim both lights
        print("\nDimming both lights to 50%...")
        ws._send_frame(json.dumps({
            "id": msg_id,
            "type": "call_service",
            "domain": "light",
            "service": "turn_on",
            "target": {"entity_id": light_entities},
            "service_data": {"brightness": 127}
        }))
        ws.message_id += 1
        
        # Wait for response and process state updates
        start_time = time.time()
        success = False
        while time.time() - start_time < 2:
            message = ws.read_message()
            if message:
                print(f"Received message: {message}")
                if message.get('id') == msg_id:
                    success = message.get('success', False)
                    print("Dim command Success!" if success else "Dim command Failed!")
            time.sleep(0.1)
            
        msg_id = ws.message_id
        
        # Turn both lights off
        print("\nTurning off both lights...")
        ws._send_frame(json.dumps({
            "id": msg_id,
            "type": "call_service",
            "domain": "light",
            "service": "turn_off",
            "target": {"entity_id": light_entities}
        }))
        ws.message_id += 1
        
        # Wait for response and process state updates
        start_time = time.time()
        success = False
        while time.time() - start_time < 2:
            message = ws.read_message()
            if message:
                print(f"Received message: {message}")
                if message.get('id') == msg_id:
                    success = message.get('success', False)
                    print("Turn off command Success!" if success else "Turn off command Failed!")
            time.sleep(0.1)
        
        # Final message processing
        start_time = time.time()
        while time.time() - start_time < 2:
            message = ws.read_message()
            if message:
                print(f"Received message: {message}")
            time.sleep(0.1)
            
    finally:
        ws.close()

def test_state_subscription():
    """Test subscribing to state changes with entity filtering"""
    print("\n=== Testing State Change Subscription ===")
    ws = HAMPWS(HA_HOST, HA_TOKEN)
    
    if not ws.connect():
        print("Failed to connect")
        return
        
    try:
        # Subscribe to state changes
        sub_id = ws.subscribe_events("state_changed")
        if sub_id:
            print("Subscribed to state changes!")
            print("Listening for state changes (Ctrl+C to stop)...")
            
            # Create set of interesting entities
            monitored_entities = set()
            for entities in [LIGHT_ENTITIES, SENSORS, CAMERAS]:
                for entity in entities.values():
                    monitored_entities.add(entity['entity_id'])
            
            # Set a timeout for the test
            start_time = time.time()
            max_duration = 30  # Run for 30 seconds
            
            while time.time() - start_time < max_duration:
                message = ws.read_message()
                if message:
                    if message.get('type') == 'event' and \
                       message.get('event', {}).get('event_type') == 'state_changed':
                        data = message['event']['data']
                        entity_id = data.get('entity_id', '')
                        
                        # Only show changes for our monitored entities
                        if entity_id in monitored_entities:
                            new_state = data.get('new_state', {}).get('state', '')
                            attributes = data.get('new_state', {}).get('attributes', {})
                            
                            # Format output based on entity type
                            if entity_id.startswith('light.'):
                                brightness = attributes.get('brightness', 0)
                                print(f"Light change: {entity_id} -> {new_state} (brightness: {brightness})")
                            elif entity_id.startswith('binary_sensor.'):
                                print(f"Sensor change: {entity_id} -> {new_state}")
                            elif entity_id.startswith('camera.'):
                                print(f"Camera change: {entity_id} -> {new_state}")
                            else:
                                print(f"State change: {entity_id} -> {new_state}")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping state subscription test...")
    finally:
        ws.close()

def test_smart_motion():
    """Test advanced motion detection with camera integration"""
    print("\n=== Testing Smart Motion Detection ===")
    ws = HAMPWS(HA_HOST, HA_TOKEN)
    
    if not ws.connect():
        print("Failed to connect")
        return
        
    try:
        # Set up trigger for motion sensor
        trigger_config = {
            "platform": "state",
            "entity_id": SENSORS['motion']['entity_id'],
            "from": "off",
            "to": "on"
        }
        
        trigger_msg_id = ws.message_id  # Store message ID for trigger subscription
        ws._send_frame(json.dumps({
            "id": trigger_msg_id,
            "type": "subscribe_trigger",
            "trigger": trigger_config
        }))
        ws.message_id += 1
        
        # Also subscribe to state changes
        state_msg_id = ws.message_id  # Store message ID for state subscription
        ws._send_frame(json.dumps({
            "id": state_msg_id,
            "type": "subscribe_events",
            "event_type": "state_changed"
        }))
        ws.message_id += 1
        
        print("Waiting for subscription confirmations...")
        
        # Track subscription states
        trigger_sub_confirmed = False
        state_sub_confirmed = False
        
        # Track entity states
        is_dark = None
        camera_state = None
        
        # Set timeouts
        start_time = time.time()
        max_duration = 30  # Run for 30 seconds
        subscription_timeout = time.time() + 5  # 5 seconds to confirm subscriptions
        
        print("Monitoring for smart motion events...")
        print("Will track motion, darkness state, and camera recording state")
        
        while time.time() - start_time < max_duration:
            message = ws.read_message()
            
            if message:
                print(f"Received message: {message}")  # Debug output
                
                # Handle subscription confirmations
                if message.get('type') == 'result':
                    msg_id = message.get('id')
                    if msg_id == trigger_msg_id and message.get('success'):
                        trigger_sub_confirmed = True
                        print("Motion trigger subscription confirmed!")
                    elif msg_id == state_msg_id and message.get('success'):
                        state_sub_confirmed = True
                        print("State change subscription confirmed!")
                
                # Once subscribed, handle events
                elif message.get('type') == 'event':
                    if message.get('event', {}).get('event_type') == 'state_changed':
                        # Track darkness and camera states
                        data = message['event']['data']
                        entity_id = data.get('entity_id', '')
                        new_state = data.get('new_state', {}).get('state', '')
                        
                        if entity_id == SENSORS['dark']['entity_id']:
                            is_dark = (new_state == 'on')
                            print(f"Darkness state: {'Dark' if is_dark else 'Light'}")
                            
                        elif entity_id == CAMERAS['back_door']['entity_id']:
                            camera_state = new_state
                            print(f"Camera state: {camera_state}")
                    
                    # Handle motion trigger events
                    elif trigger_sub_confirmed:
                        print("\nMotion detected!")
                        print(f"Current conditions:")
                        print(f"- Dark: {is_dark}")
                        print(f"- Camera: {camera_state}")
                        
                        # Automatically turn on lights if dark
                        if is_dark:
                            print("Dark condition detected - turning on lights...")
                            light_entities = [light['entity_id'] for light in LIGHT_ENTITIES.values()]
                            ws.call_service("light", "turn_on", 
                                          target={"entity_id": light_entities},
                                          service_data={"brightness": 255})
            
            # Check if subscriptions are confirmed within timeout
            if not (trigger_sub_confirmed and state_sub_confirmed):
                if time.time() > subscription_timeout:
                    print("Timeout waiting for subscription confirmations")
                    return
            
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping smart motion test...")
    finally:
        ws.close()

def main():
    """Run all tests"""
    try:
        # Test paired light control
        test_paired_lights()
        
        # Test state change subscription
        test_state_subscription()
        
        # Test smart motion detection
        test_smart_motion()
        
    except KeyboardInterrupt:
        print("\nTests stopped by user")
    except Exception as e:
        print(f"Error during tests: {e}")

if __name__ == "__main__":
    main()
