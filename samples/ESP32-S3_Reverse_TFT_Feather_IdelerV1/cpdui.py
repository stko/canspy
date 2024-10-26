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
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
# Starting in CircuitPython 9.x fourwire will be a seperate internal library
# rather than a component of the displayio library
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
# *** Choose your color display driver here ***
# ili9341 specific driver
from adafruit_st7789 import ST7789 as DISPLAY

class CPDUI:
    def __init__(self):
                
        
        # https://educ8s.tv/raspberry-pi-pico-ili9341/#google_vignette
        
        # one day of bug hunting: Display settings are stored between soft resets to
        # have a display for console outputs
        # this freezes the GPIO pin usages too and creates a "Pin in use" runtime error
        # from the second boot onwarts, when not reseting it with release_displays() at start
        
        displayio.release_displays()
        #mosi_pin = board.IO23
        #clk_pin = board.IO18
        tft_cs = board.TFT_CS
        tft_dc = board.TFT_DC
        tft_reset = board.TFT_RESET

        
        #spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
        spi = board.SPI()

        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
        
        self.display = DISPLAY( display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53)
        
        # in case the board has a display
        #self.display = board.DISPLAY
        
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




