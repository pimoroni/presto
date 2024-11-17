// Board and hardware specific configuration

#define MICROPY_HW_BOARD_NAME                   "Presto"

// Portion of onboard flash to reserve for the user filesystem
// PGA2350 has 16MB flash, so reserve 2MiB for the firmware and leave 14MiB
#define MICROPY_HW_FLASH_STORAGE_BYTES          (14 * 1024 * 1024)

// Set up networking.
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT     "PPP2"

// Enable WiFi & PPP
#define MICROPY_PY_NETWORK                      (1)
#define MICROPY_PY_NETWORK_PPP_LWIP             (1)

// CYW43 driver configuration.
#define CYW43_USE_SPI                           (1)
#define CYW43_LWIP                              (1)
#define CYW43_GPIO                              (1)
#define CYW43_SPI_PIO                           (1)

#ifndef CYW43_WL_GPIO_COUNT
#define CYW43_WL_GPIO_COUNT 3
#endif

#define MICROPY_HW_PIN_EXT_COUNT CYW43_WL_GPIO_COUNT

int mp_hal_is_pin_reserved(int n);
#define MICROPY_HW_PIN_RESERVED(i) mp_hal_is_pin_reserved(i)

// Alias the chip select pin specified by presto.h
#define MICROPY_HW_PSRAM_CS_PIN                 PIMORONI_PRESTO_PSRAM_CS_PIN

#define MICROPY_PY_THREAD                       (0)
#define MICROPY_GC_SPLIT_HEAP                   (0)

// TODO: Remove when https://github.com/micropython/micropython/pull/15655 is merged
#define core1_entry                             (NULL)