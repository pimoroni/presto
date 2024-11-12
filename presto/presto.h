/*
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

// -----------------------------------------------------
// NOTE: THIS HEADER IS ALSO INCLUDED BY ASSEMBLER SO
//       SHOULD ONLY CONSIST OF PREPROCESSOR DIRECTIVES
// -----------------------------------------------------

// This header may be included by other board headers as "boards/pimoroni_presto.h"

// pico_cmake_set PICO_PLATFORM=rp2350

#ifndef _BOARDS_PIMORONI_PRESTO_H
#define _BOARDS_PIMORONI_PRESTO_H

// For board detection
#define PIMORONI_PRESTO

// --- BOARD SPECIFIC ---
#define PIMORONI_PRESTO_PSRAM_CS_PIN 47

// --- UART ---
#ifndef PICO_DEFAULT_UART
#define PICO_DEFAULT_UART 0
#endif
#ifndef PICO_DEFAULT_UART_TX_PIN
#define PICO_DEFAULT_UART_TX_PIN 0
#endif
#ifndef PICO_DEFAULT_UART_RX_PIN
#define PICO_DEFAULT_UART_RX_PIN 1
#endif

// --- LED ---
#ifndef PICO_DEFAULT_LED_PIN
#define PICO_DEFAULT_LED_PIN 25
#endif
// no PICO_DEFAULT_WS2812_PIN

// --- I2C ---
#ifndef PICO_DEFAULT_I2C
#define PICO_DEFAULT_I2C 0
#endif
#ifndef PICO_DEFAULT_I2C_SDA_PIN
#define PICO_DEFAULT_I2C_SDA_PIN 4
#endif
#ifndef PICO_DEFAULT_I2C_SCL_PIN
#define PICO_DEFAULT_I2C_SCL_PIN 5
#endif

// --- SPI ---
#ifndef PICO_DEFAULT_SPI
#define PICO_DEFAULT_SPI 0
#endif
#ifndef PICO_DEFAULT_SPI_SCK_PIN
#define PICO_DEFAULT_SPI_SCK_PIN 18
#endif
#ifndef PICO_DEFAULT_SPI_TX_PIN
#define PICO_DEFAULT_SPI_TX_PIN 19
#endif
#ifndef PICO_DEFAULT_SPI_RX_PIN
#define PICO_DEFAULT_SPI_RX_PIN 16
#endif
#ifndef PICO_DEFAULT_SPI_CSN_PIN
#define PICO_DEFAULT_SPI_CSN_PIN 17
#endif

// --- FLASH ---

#define PICO_BOOT_STAGE2_CHOOSE_W25Q080 1

#ifndef PICO_FLASH_SPI_CLKDIV
#define PICO_FLASH_SPI_CLKDIV 2
#endif

// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (16 * 1024 * 1024)
#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (16 * 1024 * 1024)
#endif

// --- WIRELESS ---

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_REG_ON, gpio pin to power up the cyw43 chip, type=int, default=23, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_REG_ON
#define CYW43_DEFAULT_PIN_WL_REG_ON 23u
#endif

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_DATA_OUT, gpio pin for spi data out to the cyw43 chip, type=int, default=24, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_DATA_OUT
#define CYW43_DEFAULT_PIN_WL_DATA_OUT 24u
#endif

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_DATA_IN, gpio pin for spi data in from the cyw43 chip, type=int, default=24, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_DATA_IN
#define CYW43_DEFAULT_PIN_WL_DATA_IN 24u
#endif

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_HOST_WAKE, gpio (irq) pin for the irq line from the cyw43 chip, type=int, default=24, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_HOST_WAKE
#define CYW43_DEFAULT_PIN_WL_HOST_WAKE 24u
#endif

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_CLOCK, gpio pin for the spi clock line to the cyw43 chip, type=int, default=29, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_CLOCK
#define CYW43_DEFAULT_PIN_WL_CLOCK 29u
#endif

// PICO_CONFIG: CYW43_DEFAULT_PIN_WL_CS, gpio pin for the spi chip select to the cyw43 chip, type=int, default=25, advanced=true, group=pico_cyw43_driver
#ifndef CYW43_DEFAULT_PIN_WL_CS
#define CYW43_DEFAULT_PIN_WL_CS 25u
#endif

// no PICO_SMPS_MODE_PIN
// no PICO_VBUS_PIN
// no PICO_VSYS_PIN

#ifndef PICO_RP2350_A2_SUPPORTED
#define PICO_RP2350_A2_SUPPORTED 1
#endif

#endif
