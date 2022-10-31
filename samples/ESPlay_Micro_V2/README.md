# CANSpy auf einem ESPlay Micro V2

## Setup 
Unter Unbuntu 22.04 wird der ch341-uart des ESPLay dummerweise für ein Braille- Device gehalten, und weil das Braille- Device dann nicht richtig initialiert werden kann, wirft der Braille- Treiber das ganze ttyUSB0- Device wieder raus 

Abhilfe für Ubuntu 22.04:
  sudo apt remove brltty



## Reparieren des Bootloaders

Wenn sich aus unerfindlichen Gründen der Bootloader verabschiedet haben soll, kann man ihn glücklicherweise durch Neuflashen wieder herstellen - Schwein gehabt! https://github.com/pebri86/esplay-base-firmware/releases/tag/v1.0-esplay-micro

## Boot-Image selbst gebaut

In Verzeichnis `make_fw` ist beschrieben, wie man sich eigene Boot- Images bauen kann.

Die fertigen Firmware- Images *.fw (selbstgemacht oder fertig) gehören dann auf der SD-Karte ins  `/esplay/firmware`- Verzeichnis, um vom Bootloader gefunden zu werden. Fertige Images gibts auch auf https://github.com/pebri86/esplay-micro-firmware-collections

## Installation of the Graphics Driver
CANSpy is using the nano-gui micropython graphics library, which is available for a brought range of systems. When using it, it needs a little bit of setup and configuration, which is explained here for the ESPlay Micro 2 and its 2,4" ILI9341 TFT Panel. Other displays on other systems would be simular.

Get a copy of the latest driver

    git clone --depth=1 https://github.com/peterhinch/micropython-nano-gui
    

Delete all unused files and dirs, keep just the driver and the gui directory (and the images for the demos)

    rm -vr !("drivers"|"gui"|"images")
    cd drivers
    rm -vr !("ili93xx"|"boolpalette.py")
    cd ..



Save the following code snipplet as `color_setup.py`

```
# color_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on ESP32
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# ESP   SSD
# 3v3   Vin
# Gnd   Gnd
pin_DC   = 12   # IO12  DC  
pin_CS   =  5   # IO05  CS

'''
On ESPlay, the display reset signal is not connected to the controller,
but the ili9341 driver wants to sent a reset at __init__, so we sent 
this signal to the Backlight output in the hope that this will not cause some
trouble...
'''
pin_Rst  = 27   # IO27  Rst  (the missused backlight BCKL)

pin_CLK  = 18   # IO18  CLK  Hardware SPI1
pin_MOSI = 23   # IO23  DATA (AKA SI MOSI)
pin_MISO = 19   # IO19  DATA (AKA SI MISO)

from machine import Pin, SPI
import gc

# *** Choose your color display driver here ***
# ili9341 specific driver
from drivers.ili93xx.ili9341 import ILI9341 as SSD

pdc = Pin( pin_DC , Pin.OUT, value=0)  # Arbitrary pins
pcs = Pin( pin_CS , Pin.OUT, value=1)
prst = Pin( pin_Rst , Pin.OUT, value=1)

# Kept as ssd to maintain compatability
gc.collect()  # Precaution before instantiating framebuf
spi = SPI(1, 10_000_000, sck=Pin( pin_CLK ), mosi=Pin( pin_MOSI ), miso=Pin( pin_MISO ))
ssd = SSD(spi, dc=pdc, cs=pcs, rst=prst, usd= True)
```

install the `rshell` tool

    pip3 install rshell

start `rshell` and connect to the board

    connect serial /dev/ttyUSB0

verify your found board name

    boards

transfer the gui files - here the board name was shown as `pyboard` in the `boards` command

    cp -r drivers /pyboard
    cp -r gui /pyboard
    cp color_setup.py /pyboard

enter the `repl`

    repl

and fire the graphic demo

    import gui.demos.aclock

