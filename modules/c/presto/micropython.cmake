add_library(usermod_presto INTERFACE)

get_filename_component(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}../../../../" ABSOLUTE)

target_sources(usermod_presto INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/presto.c
    ${CMAKE_CURRENT_LIST_DIR}/presto.cpp
    ${REPO_ROOT}/drivers/st7701/st7701.cpp
)
pico_generate_pio_header(usermod_presto ${REPO_ROOT}/drivers/st7701/st7701_parallel.pio)
pico_generate_pio_header(usermod_presto ${REPO_ROOT}/drivers/st7701/st7701_timing.pio)
pico_generate_pio_header(usermod_presto ${REPO_ROOT}/drivers/st7701/st7701_palette.pio)

set_source_files_properties(${REPO_ROOT}/drivers/st7701/st7701.cpp PROPERTIES COMPILE_OPTIONS "-O2;-fgcse-after-reload;-floop-interchange;-fpeel-loops;-fpredictive-commoning;-fsplit-paths;-ftree-loop-distribute-patterns;-ftree-loop-distribution;-ftree-vectorize;-ftree-partial-pre;-funswitch-loops")

target_include_directories(usermod_presto INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${PIMORONI_PICO_PATH}/libraries/pico_graphics/
    ${REPO_ROOT}/drivers/st7701/
    ${REPO_ROOT}/micropython/modules
)

target_link_libraries(usermod INTERFACE usermod_presto)