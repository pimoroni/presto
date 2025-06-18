# Pimoroni Presto<!-- omit in toc -->

## RP2350-powered 4" touchscreen display with RGB ambient lighting<!-- omit in toc -->

This repository is home to the MicroPython firmware and examples for
Pimoroni Presto.

- [Get Pimoroni Presto](#get-pimoroni-presto)
- [Download Firmware](#download-firmware)
- [Installation](#installation)
- [Useful Links](#useful-links)
- [Other Resources](#other-resources)

## Get Pimoroni Presto

* [Pimoroni Presto](https://shop.pimoroni.com/products/presto)

## Download Firmware

You can find the latest firmware releases at [https://github.com/pimoroni/presto/releases/latest](https://github.com/pimoroni/presto/releases/latest).

There are two choices, a regular build that just updates the MicroPython firmware and a "-with-examples" build which includes everything in [examples](examples).

:warning: If you've changed any of the code on your board then back up before flashing "-with-examples" - *your files will be erased!*

## Installation

1. Connect Presto to your computer with a USB-C cable.
2. Put your device into bootloader mode by holding down the BOOT button whilst tapping RESET.
3. Drag and drop the downloaded .uf2 file to the "RP2350" drive that appears.
4. Your device should reset, and you should then be able to connect to it using [Thonny](https://thonny.org/).

## Useful Links

* [Learn: Getting Started with Presto](https://learn.pimoroni.com/article/getting-started-with-presto)
* [Function Reference](docs/presto.md)
* [Pico Graphics documentation](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/picographics/README.md)
* [Pico Vector documentation](docs/picovector.md)
* [EzWiFi documentation](docs/wifi.md)

## Other Resources

Links to community projects and other resources that you might find helpful can be found below. Note that these code examples have not been written/tested by us and we're not able to offer support with them.

- PrestoDeck (Spotify Music Player) - [Youtube](https://www.youtube.com/watch?v=iOz5XUVkFkY) / [Github](https://github.com/fatihak/PrestoDeck)
- [Last.fm Now Playing Display](https://github.com/andypiper/presto-lastfm)
- [PrestoMaze - maze generation and solving](https://github.com/kurosuke/PrestoMaze/)
- [Presto Stream Deck Controller](https://forums.pimoroni.com/t/presto-stream-deck-controller/27930)



