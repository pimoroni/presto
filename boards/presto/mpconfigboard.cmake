# cmake file for the Pimoroni PGA2350
set(PICO_BOARD "presto")
set(PICO_PLATFORM "rp2350-arm-s")
set(PICO_NUM_GPIOS 48)

# Make sure we find pga2350.h (PICO_BOARD) in the current dir
set(PICO_BOARD_HEADER_DIRS ${CMAKE_CURRENT_LIST_DIR})

# Portion of onboard flash to reserve for the user filesystem.
# Presto has 16MB flash, so reserve 2MiB for the firmware and leave 14MiB.
set(MICROPY_HW_FLASH_STORAGE_BYTES 14680064)

# Board specific version of the frozen manifest
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)

# 8MB PSRAM on GPIO47. Links hardware_psram and brings PSRAM up in runtime_init.
set(MICROPY_HW_ENABLE_PSRAM 1)
set(MICROPY_HW_PSRAM_CS_PIN 47)

# If USER_C_MODULES or MicroPython customisations use malloc then
# there needs to be some RAM reserved for the C heap
set(MICROPY_C_HEAP_SIZE 4096)

# Links micropy_lib_lwip and sets MICROPY_PY_LWIP = 1
# Picked up and expanded upon in mpconfigboard.h
set(MICROPY_PY_LWIP ON)

# Links cyw43-driver and sets:
# MICROPY_PY_NETWORK_CYW43 = 1,
# MICROPY_PY_SOCKET_DEFAULT_TIMEOUT_MS = 30000
set(MICROPY_PY_NETWORK_CYW43 ON)

# Adds mpbthciport.c
# And sets:
# MICROPY_PY_BLUETOOTH = 1,
# MICROPY_PY_BLUETOOTH_USE_SYNC_EVENTS = 1,
# MICROPY_PY_BLUETOOTH_ENABLE_CENTRAL_MODE = 1
set(MICROPY_PY_BLUETOOTH ON)

# Links pico_btstack_hci_transport_cyw43
# And sets:
# MICROPY_BLUETOOTH_BTSTACK = 1,
# MICROPY_BLUETOOTH_BTSTACK_CONFIG_FILE =
set(MICROPY_BLUETOOTH_BTSTACK ON)

# Sets:
# CYW43_ENABLE_BLUETOOTH = 1,
# MICROPY_PY_BLUETOOTH_CYW43 = 1
set(MICROPY_PY_BLUETOOTH_CYW43 ON)

set(MICROPY_BOARD_LINKER_SCRIPT ${MICROPY_BOARD_DIR}/presto.ld)

# Board specific version of the frozen manifest
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)

set(PIMORONI_UF2_MANIFEST ${MICROPY_BOARD_DIR}/manifest.txt)
set(PIMORONI_UF2_DIR ${CMAKE_CURRENT_LIST_DIR}/../../examples)
include(${CMAKE_CURRENT_LIST_DIR}/../common.cmake)