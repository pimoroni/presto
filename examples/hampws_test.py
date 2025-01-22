from config import (
    HA_HOST, HA_TOKEN, 
    LIGHT_ENTITIES, SENSORS, CAMERAS
)
from hampws import HAMPWS
import time
import json

# Try to import and initialize Presto
try:
    import presto
    presto_context = presto.Presto()
    PRESTO_AVAILABLE = True
    print("Presto system initialized successfully")
except (ImportError, Exception) as e:
    print(f"Presto not available: {e}")
    PRESTO_AVAILABLE = False
    presto_context = None

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
        
        # Turn both lights on
        print(f"\nTurning on both back door lights...")
        success = ws.call_service("light", "turn_on", 
                                target={"entity_id": light_entities},
                                service_data={"brightness": 255})
        print("Success!" if success else "Failed!")
        
        time.sleep(2)  # Wait to see the change
        
        # Dim both lights
        print("\nDimming both lights to 50%...")
        success = ws.call_service("light", "turn_on", 
                                target={"entity_id": light_entities},
                                service_data={"brightness": 127})
        print("Success!" if success else "Failed!")
        
        time.sleep(2)
        
        # Turn both lights off
        print("\nTurning off both lights...")
        success = ws.call_service("light", "turn_off", 
                                target={"entity_id": light_entities})
        print("Success!" if success else "Failed!")
        
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
            
            while True:
                message = ws.read_message()
                if not message:
                    print("Connection closed")
                    break
                    
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
        # Set up trigger for motion sensor AND darkness sensor
        trigger_config = {
            "platform": "state",
            "entity_id": SENSORS['motion']['entity_id'],
            "from": "off",
            "to": "on"
        }
        
        sub_id = ws.subscribe_trigger(trigger_config)
        if sub_id:
            print("Motion trigger subscription successful!")
            
            # Also subscribe to state changes for darkness sensor and camera
            state_sub_id = ws.subscribe_events("state_changed")
            if not state_sub_id:
                print("Failed to subscribe to state changes")
                return
                
            print("Monitoring for smart motion events (Ctrl+C to stop)...")
            print("Will track motion, darkness state, and camera recording state")
            
            # Track states
            is_dark = None
            camera_state = None
            
            while True:
                message = ws.read_message()
                if not message:
                    print("Connection closed")
                    break
                    
                if message.get('type') == 'event':
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
                            
                    else:
                        # Handle motion trigger
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
        #   - exception if no SENSORS in config
        test_smart_motion()
        
    except KeyboardInterrupt:
        print("\nTests stopped by user")
    except Exception as e:
        print(f"Error during tests: {e}")

if __name__ == "__main__":
    main()