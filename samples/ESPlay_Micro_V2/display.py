'''
this display module is the wrapper to display the information table on whatever diplay we have
'''

# this is a nano-gui driver, made out of the demos/Label Demo


# Initialise hardware and framebuf before importing modules.
from color_setup import ssd  # Create a display instance
from gui.core.nanogui import refresh
from gui.core.writer import CWriter
from gui.core.colors import *

from gui.widgets.label import Label
import gui.fonts.arial35 as arial35

from micropython import const


class Display:
    def __init__(self):
        # a few constants
        self.row_height = const(37)
        # on the ESPlay the leftmost pixels are hidden under the front plate :-(
        self.left_padding = const(5)
        self.top_padding = const(0)
        # available rows minus title
        self.nr_of_rows = const(
            (ssd.height - self.top_padding)//self.row_height - 1)
        print("nr of rows", self.nr_of_rows)
        # In case previous tests have altered it
        CWriter.set_textpos(ssd, 0, 0)
        # create the list of LABELS to show the text in it
        self.labels = [Label(CWriter(ssd, arial35, WHITE, BLUE, verbose=False), self.top_padding,
                             self.left_padding, ssd.width - self.left_padding-2)]  # we init the labels with the title label
        normal_writer = CWriter(ssd, arial35, BLACK, WHITE, verbose=False)
        for i in range(self.nr_of_rows):
            print("coords:", self.left_padding, self.top_padding + (
                i+1) * self.row_height)
            self.labels.append(Label(normal_writer,  self.top_padding + (
                i+1) * self.row_height, self.left_padding, ssd.width - self.left_padding-2))
        #self.normalwriter.set_clip(True, True, False)
        self.clear()
        # refresh(ssd)  # Initialise and clear display.
        ssd.fill(255)
        return
        # make sure the image has the right size !
        # it can be made with
        #    ffmpeg -loglevel error -i my_splash_image -f rawvideo -pix_fmt rgb565 "splash.rgb565"
        # make sure the image has the right size
        f = open('splash.rgb565', 'rb')
        for x in range(ssd.height):
            print(x)
            for y in range(ssd.width):
                c = int.from_bytes(f.read(2), 'little')
                ssd.pixel(y, x, c)
        ssd.show()

    def clear(self):
        self.cursor_pos = 0
        self.last_id = None
        self.last_content = None
        for label in self.labels:
            label.value("")

    def show(self, content, title):

        self.labels[0].value(title)
        if not self.last_content:  # this is the first call
            pass
        for title, format_telegram in content.items():
            print(title, format_telegram.text)
        refresh(ssd)

    def show_splash(self):
        self.clear()
        self.labels[self.nr_of_rows/2].value('Scan for Buses')
        refresh(ssd)
