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