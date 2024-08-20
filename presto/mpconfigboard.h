// Board and hardware specific configuration

#define MICROPY_HW_BOARD_NAME                   "Presto"

// Portion of onboard flash to reserve for the user filesystem
// PGA2350 has 16MB flash, so reserve 2MiB for the firmware and leave 14MiB
#define MICROPY_HW_FLASH_STORAGE_BYTES          (14 * 1024 * 1024)

// Alias the chip select pin specified by presto.h
#define MICROPY_HW_PSRAM_CS_PIN                 PIMORONI_PRESTO_PSRAM_CS_PIN
#define MICROPY_HW_ENABLE_PSRAM                 (1)

#define MICROPY_PY_THREAD                       (0)

// TODO: Remove when https://github.com/micropython/micropython/pull/15655 is merged
#define core1_entry                             (NULL)

// Enable networking.
#define MICROPY_PY_NETWORK 1
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT     MICROPY_HW_BOARD_NAME

// CYW43 driver configuration.
#define CYW43_USE_SPI (1)
#define CYW43_LWIP (1)
#define CYW43_GPIO (1)
#define CYW43_SPI_PIO (1)

// For debugging mbedtls - also set
// Debug level (0-4) 1=warning, 2=info, 3=debug, 4=verbose
// #define MODUSSL_MBEDTLS_DEBUG_LEVEL 1