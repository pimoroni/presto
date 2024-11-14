# https://github.com/micropython/micropython-lib/blob/master/micropython/bundles/bundle-networking/manifest.py
require("bundle-networking")
require("urllib.urequest")
require("umqtt.simple")

# Handy for dealing with APIs
require("datetime")

# SD Card
require("sdcard")

# Bluetooth
require("aioble")

# Include the manifest.py from micropython/ports/rp2/boards/manifest.py
include("$(PORT_DIR)/boards/manifest.py")

# Include the manifest.py from micropython/<board>/manifest.py
include("$(BOARD_DIR)/manifest.py")

# Include pga/modules/py_frozen
freeze("py_frozen/")
