# config.py
#
# ip address and port of your home assistant instance
HA_HOST = "http://192.168.1.24:8123"
#
# tokens are created in the home assistant interfacea interface - when logged in:
# Click bottom left on name
#   -> Security tab
#   -> scroll down
#   -> Create token
HA_TOKEN = ""
#
# entities such as light.back_door must exist in your home assistant instance
# Settings
#   -> Devices and services
#   -> Entities tab
#   -> Entity ID

# Light entities
LIGHT_ENTITIES = {
    "back_door": {
        "entity_id": "light.back_door",
        "display_name": "Back Door Light 1"
    },
    "back_door_2": {
        "entity_id": "light.back_door_2",
        "display_name": "Back Door Light 2"
    }
}

# Sensor entities
SENSORS = {
    "motion": {
        "entity_id": "binary_sensor.back_door_02_motion",
        "display_name": "Back Door Motion"
    },
    "dark": {
        "entity_id": "binary_sensor.back_door_02_is_dark",
        "display_name": "Back Door Darkness"
    },
    "voltage": {
        "entity_id": "sensor.back_door_02_voltage",
        "display_name": "Back Door Voltage"
    }
}

# Camera entities
CAMERAS = {
    "back_door": {
        "entity_id": "camera.back_door_02_high_resolution_channel",
        "display_name": "Back Door Camera"
    }
}