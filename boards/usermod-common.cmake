if(NOT DEFINED PIMORONI_PICO_PATH)
set(PIMORONI_PICO_PATH ${CMAKE_CURRENT_LIST_DIR}/../pimoroni-pico)
endif()
include(${PIMORONI_PICO_PATH}/pimoroni_pico_import.cmake)

include_directories(${CMAKE_CURRENT_LIST_DIR}/..)
include_directories(${PIMORONI_PICO_PATH}/micropython)

list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython")
list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython/modules")

# Allows us to find /modules/c/<module>/micropython
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/..")

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

include(modules/c/presto/micropython)

# Essential
include(pimoroni_i2c/micropython)
include(pimoroni_bus/micropython)

# PicoVector & MicroPython bindings.
# Core1 runs the ST7701 scanout, so the rasteriser stays on core0.
set(PV_DUAL_CORE OFF)
find_package(PICOVECTOR_MICROPYTHON CONFIG REQUIRED)

include(qrcode/micropython/micropython)

# Sensors & Breakouts
include(micropython-common-breakouts)

# Utility
include(adcfft/micropython)

# LEDs & Matrices
include(plasma/micropython)

# ULAB
include(micropython-common-ulab)
enable_ulab()

include(modules_py/modules_py)

# C++ Magic Memory
include(cppmem/micropython)
target_compile_definitions(usermod INTERFACE
    CPP_FIXED_HEAP_SIZE=256)

# Disable build-busting C++ exceptions
include(micropython-disable-exceptions)