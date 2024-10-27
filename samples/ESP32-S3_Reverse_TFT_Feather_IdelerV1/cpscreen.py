"""
circuitpython class for all screen related primitives in displayio
"""

import time
import adafruit_display_text
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import board
import os
import displayio
import bitmaptools
import terminalio
import digitalio
import busio
from adafruit_display_text import label
#from adafruit_display_shapes.rect import Rect
import terminalio

from random import randrange
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

from ascreen import AScreen


class Screen(AScreen):
    """
    provides all graphics primitives and other informations to

    colors see https://wiki.tcl-lang.org/page/Colors+with+Names?R=0&O=Named+Colors&W=
    """

    FONT_SIZE = 8
    FONT_NAME = "arial"
    FONT_SIZE = 16
    FONT_WEIGHT = "normal"
    BACKGROUND = 0
    TITLE_BG = 1
    TITLE_PERCENT = 2
    TITLE_COLOR = 3
    TEXT_BG = 4
    TEXT_PERCENT = 5
    TEXT_COLOR = 6
    VALUE_COLOR = 7
    MARKER_BACK = 8
    MARKER_SELECT = 9
    MARKER_UP = 10
    MARKER_DOWN = 11
    MARKER_INACTIVE = 12

    def __init__(
        self,
        title: str,
        width: int,
        height: int,
        padding: int = 1,
        gap: int = 1,
        marker_width: int = 2,
        orientation: int = 0,
        move_cursor=None,
        back=None,
        select=None,
        eval_mouse_move=None,
        font_size=FONT_SIZE,
        font_file = "fonts/LeagueSpartan-Bold-16.bdf"
    ):
        




        self.run = True
        ## the board specific stuff

        # displayio uses a color palette, so we've to assign our colors to a palette_

        self.palette = displayio.Palette(13)
        self.palette[self.BACKGROUND] = displayio.ColorConverter().convert(0xcdb5cd) # "thistle3"
        self.palette[self.TITLE_BG] = displayio.ColorConverter().convert(0x600909) # "cornflower blue"
        self.palette[self.TITLE_PERCENT] = displayio.ColorConverter().convert(0x0000ee) # "blue2"
        self.palette[self.TITLE_COLOR] = displayio.ColorConverter().convert(0xffffff) # "white"
        self.palette[self.TEXT_BG] = displayio.ColorConverter().convert(0x76ee) # "chartreuse2"
        self.palette[self.TEXT_PERCENT] = displayio.ColorConverter().convert(0xffd700) # "gold"
        self.palette[self.TEXT_COLOR] = displayio.ColorConverter().convert(0x000000) # "black"
        self.palette[self.VALUE_COLOR] = displayio.ColorConverter().convert(0x0000ff) # "blue"
        self.palette[self.MARKER_BACK] = displayio.ColorConverter().convert(0x0000ee) # "blue2"
        self.palette[self.MARKER_SELECT] = displayio.ColorConverter().convert(0xee0000) # "red2"
        self.palette[self.MARKER_UP] = displayio.ColorConverter().convert(0x00cd00) # "green3"
        self.palette[self.MARKER_DOWN] = displayio.ColorConverter().convert(0xeeee00) # "yellow2"
        self.palette[self.MARKER_INACTIVE] = displayio.ColorConverter().convert(0x030303) # "grey"]
        
        # uncomment the next block in case the board has a predefined display
        """

        # https://educ8s.tv/raspberry-pi-pico-ili9341/#google_vignette
        
        # one day of bug hunting: Display settings are stored between soft resets to
        # have a display for console outputs
        # this freezes the GPIO pin usages too and creates a "Pin in use" runtime error
        # from the second boot onwarts, when not reseting it with release_displays() at start
        

        # do NOT USE release_displays() on boards with build in circuitpython board.DISPLAY,
        as it will also reset these internal device and then there is no display anymore..

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
        """
        # in case the board has a display
        self.display = board.DISPLAY
        self.display.auto_refresh = False
        self.font =  bitmap_font.load_font(font_file)
        self.font_size = font_size
        self.font_height = font_size
        self.descent=0
        # Make the display context
        
        main_group = displayio.Group()
        #print (board.name)
        #print (self.display)



        self.bitmap = displayio.Bitmap(self.display.width,self.display.height, 13)
        self.bitmap.fill(0)

        #bitmaptools.circle(64,64, 32, 1)
        
        tilegrid = displayio.TileGrid(bitmap=self.bitmap, pixel_shader=self.palette)
        main_group.append(tilegrid)
        self.display.root_group = main_group
        bitmaptools.fill_region(self.bitmap,10,10,100,100,5)
        text_bitmap=bitmap_label.Label(font=self.font,text="bla",color=0xffffff,save_text=False)
        bitmaptools.blit(self.bitmap,text_bitmap.bitmap,10,10)
        #self.display.root_group=text_bitmap
        print(self.bitmap.width)
        print(self.bitmap.height)
        print(self.bitmap.bits_per_value)
        print(text_bitmap.height)
        print(text_bitmap.width)
        print(text_bitmap.bitmap.bits_per_value)
        print("end of Display init")



        super().__init__(
            width,
            height,
            self.font_height,
            padding,
            gap,
            marker_width,
            orientation,
            move_cursor,
            back,
            select,
            eval_mouse_move,
        )

    def quit(self):
        self.run = False

    def start(self, loop):
        """
        must be start after all the initial layout has been made
        to let the UI do their event handling

        """
        self.loop = loop
        # as displayIO does not have its own main event loop (in opposite to e.g. tkinter)
        # we just call the custom loop here in a (nearly) endless loop
        if loop:
            while self.run:
                loop()

    # catch the mouse evetns
    def start_tk_mouse_move(self, event):
        """transforms tk mouse event into x,y coords"""
        super().start_mouse_move(event.x, event.y)

    def stop_tk_mouse_move(self, event):
        """transforms tk mouse event into x,y coords"""
        if self.mouse_move:
            super().stop_mouse_move(event.x, event.y)

    # catch the keyboard events
    def onKeyPress(self, event):
        if event.keysym == "Up" and self.move_cursor:
            self.move_cursor(-1)
        if event.keysym == "Down" and self.move_cursor:
            self.move_cursor(1)
        if event.keysym == "Left" and self.back:
            self.back()
        if event.keysym == "Right" and self.select:
            self.select()

    # graphic primitives for rectangles and text
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color):
        x1, x2 = self.lower_first(x1,x2)
        y1, y2 = self.lower_first(y1,y2)

        print("rect", x1, y1, x2, y2, color,)
        bitmaptools.fill_region(self.bitmap,x1, y1, x2, y2, color)
        #self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=0)

    def draw_text(
        self,
        text: str,
        x,
        y,
        color: int,
        font_name: str,
        font_size: int,
        font_weight: str,
        orientation="sw",
    ):

        text_bitmap=bitmap_label.Label(font=self.font,text=text,color=self.palette[color],save_text=False,background_color=None)
        print("text",x,y, color, hex(self.palette[color]), text)
        if text_bitmap.bitmap:
            if orientation=="sw":
                bitmaptools.blit(self.bitmap,text_bitmap.bitmap,x,y-text_bitmap.bitmap.height)
            else:
                bitmaptools.blit(self.bitmap,text_bitmap.bitmap,x-text_bitmap.bitmap.width,y-text_bitmap.bitmap.height)


    def refresh(self):
        self.display.refresh()

    def text(self, row: int, title: str, value: str, percent: int = 0, refresh=False):
        if row > self.nr_of_rows:
            return
        x1, y1, x2, y2 = self.frame_coords(row)
        if percent:  # draw two bars
            x_middle = (x2 - x1) * percent // 100
            if row == 0:
                self.draw_rectangle(x1, y1, x_middle, y2, self.TITLE_PERCENT)
                self.draw_rectangle(x_middle, y1, x2, y2, self.TITLE_BG)

            else:
                self.draw_rectangle(x1, y1, x_middle, y2, self.TEXT_PERCENT)
                self.draw_rectangle(x_middle, y1, x2, y2, self.TEXT_BG)
        else:
            if row == 0:
                self.draw_rectangle(x1, y1, x2, y2, self.TITLE_BG)
            else:
                self.draw_rectangle(x1, y1, x2, y2, self.TEXT_BG)

        x, y = self.text_start(row)
        output = [
            title,
            value,
        ]  # beeing lazy and write the whole textformating just once...
        for i in range(2):
            content = output[i]
            if row == 0:
                color = self.TITLE_COLOR
            else:
                color = self.TEXT_COLOR
            if i == 0:
                self.draw_text(
                    content,
                    x,
                    y - self.descent,
                    color,
                    self.FONT_NAME,
                    self.FONT_SIZE,
                    self.FONT_WEIGHT,
                )
            else:
                self.draw_text(
                    content,
                    self.actual_width - self.marker_width - self.gap - self.padding,
                    y - self.descent,
                    self.VALUE_COLOR,
                    self.FONT_NAME,
                    self.FONT_SIZE,
                    self.FONT_WEIGHT,
                    orientation="se",
                )
        if refresh:
            self.refresh()

    def close(self):
        self.quit()