add_library(st7701_presto INTERFACE)

target_sources(st7701_presto INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/st7701.cpp)

pico_generate_pio_header(st7701_presto ${CMAKE_CURRENT_LIST_DIR}/st7701_parallel.pio)
pico_generate_pio_header(st7701_presto ${CMAKE_CURRENT_LIST_DIR}/st7701_timing.pio)
pico_generate_pio_header(st7701_presto ${CMAKE_CURRENT_LIST_DIR}/st7701_palette.pio)

target_include_directories(st7701_presto INTERFACE ${CMAKE_CURRENT_LIST_DIR})

# Pull in pico libraries that we need
target_link_libraries(st7701_presto INTERFACE pico_stdlib pimoroni_bus hardware_spi hardware_pwm hardware_pio hardware_dma pico_graphics)
