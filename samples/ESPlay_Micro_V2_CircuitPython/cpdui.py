'''
CPDUI - the Circuitpython device User interface

This should be the framework to give iot devices a common user interface

the devices uses the cp buildin feature to connect to a wifi network defined in settings.toml

if the MQTT_xxx settings are given, it connect to the mqtt server too


'''
import board
import os
import displayio
import terminalio
import digitalio
import busio
import adafruit_ili9341
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout

# *** Choose your color display driver here ***
# ili9341 specific driver
from adafruit_ili9341 import ILI9341 as DISPLAY

class CPDUI:
    def __init__(self):
                
        
        # https://educ8s.tv/raspberry-pi-pico-ili9341/#google_vignette
        
        # one day of bug hunting: Display settings are stored between soft resets to
        # have a display for console outputs
        # this freezes the GPIO pin usages too and creates a "Pin in use" runtime error
        # from the second boot onwarts, when not reseting it with release_displays() at start
        
        
        displayio.release_displays()
        mosi_pin = board.IO23
        clk_pin = board.IO18
        cs_pin = board.IO5
        dc_pin = board.IO12
        '''
        On ESPlay, the display reset signal is not connected to the controller,
        but the ili9341 driver wants to sent a reset at __init__, so we sent 
        this signal to the Backlight output in the hope that this will not cause some
        trouble...
        '''
        reset_pin = board.IO27
        
        spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
        
        display_bus = displayio.FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)
        
        self.display = DISPLAY(display_bus, width=240, height=320, rotation=0)
        
        # in case the board has a display
        # self.display = board.DISPLAY
        
        # Make the display context
        
        main_group = displayio.Group()
        self.display.root_group = main_group
        print("end of init")
        
    def draw(self):
        print("draw 1")
        
        layout = GridLayout(
            x=10,
            y=10,
            width=200,
            height=100,
            grid_size=(2, 2),
            cell_padding=8,
        )
        _labels = []
        
        
        _labels.append(
            label.Label(
                terminalio.FONT, scale=2, x=0, y=0, text="Hello", background_color=0x770077
            )
        )
        
        layout.add_content(_labels[0], grid_position=(0, 0), cell_size=(1, 1))
        _labels.append(
            label.Label(
                terminalio.FONT, scale=2, x=0, y=0, text="World", background_color=0x007700
            )
        )
        
        layout.add_content(_labels[1], grid_position=(1, 0), cell_size=(1, 1))
        _labels.append(label.Label(terminalio.FONT, scale=2, x=0, y=0, text="Hello"))
        layout.add_content(_labels[2], grid_position=(0, 1), cell_size=(1, 1))
        _labels.append(label.Label(terminalio.FONT, scale=2, x=0, y=0, text="Grid"))
        layout.add_content(_labels[3], grid_position=(1, 1), cell_size=(1, 1))
        
        self.display.root_group.append(layout)
        print("draw 2")




