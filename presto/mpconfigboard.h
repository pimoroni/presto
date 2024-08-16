// Board and hardware specific configuration

#define MICROPY_HW_BOARD_NAME                   "Presto"

// Portion of onboard flash to reserve for the user filesystem
// PGA2350 has 16MB flash, so reserve 2MiB for the firmware and leave 14MiB
#define MICROPY_HW_FLASH_STORAGE_BYTES          (14 * 1024 * 1024)

// Alias the chip select pin specified by presto.h
#define MICROPY_HW_PSRAM_CS_PIN                 PIMORONI_PRESTO_PSRAM_CS_PIN
#define MICROPY_HW_ENABLE_PSRAM                 (1)

#define MICROPY_PY_THREAD                       (0)
#define MICROPY_GC_SPLIT_HEAP                   (0)

// TODO: Remove when https://github.com/micropython/micropython/pull/15655 is merged
#define core1_entry                             (NULL)