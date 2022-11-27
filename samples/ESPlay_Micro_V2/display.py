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
        self.row_height = const(38)
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
        self.clear("")
        # refresh(ssd)  # Initialise and clear display.
        ssd.fill(255)

        # uncomment the return to avoid the splash screen
        # #return

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

    def clear(self, title):
        self.cursor_list_pos = 0
        self.cursor_row_pos = 0
        self.last_id = None
        for label in self.labels:
            label.value("")
        self.labels[0].value(title)

    def get_cursor_pos(self, ids_list):
        cursor_list_pos = 0
        if not self.last_id:  # no last_id? Then we are just beginning
            return 0
        # looking at which position in the list we are
        while cursor_list_pos < len(ids_list)-1 and not self.last_id == ids_list[cursor_list_pos]:
            cursor_list_pos += 1
        return cursor_list_pos

    def show(self, content, cursormove=0):
        '''
        This routine builds the screen - and when cursormove is <>0 , it moves the cursor up and down
        '''
        if not content:
            self.clear("")
            return
        # makes a indexable list out of the content title keys
        ids_list = sorted(list(content))
        if not self.last_id:  # this is the first call
            pass # self.last_id = ids_list[0]
        cursor_list_pos = self.get_cursor_pos(ids_list)

        if cursormove != 0:
            new_cursor_list_pos = cursor_list_pos + cursormove
            if new_cursor_list_pos > -1 and new_cursor_list_pos < len(ids_list):
                cursor_list_pos = new_cursor_list_pos
                self.last_id = ids_list[cursor_list_pos]
                self.cursor_row_pos += cursormove
                self.cursor_row_pos = min(
                    self.cursor_row_pos, self.nr_of_rows-1)
                self.cursor_row_pos = max(self.cursor_row_pos, 0)
            elif new_cursor_list_pos < 0:  # jump to end if list
                cursor_list_pos = len(ids_list)-1
                self.last_id = ids_list[cursor_list_pos]
                self.cursor_row_pos = self.nr_of_rows-1
            else:  # jump to beginning of list
                cursor_list_pos = 0
                self.last_id = ids_list[cursor_list_pos]
                self.cursor_row_pos = 0

        '''
        now we can fill the display. Luckely a content list can only get longer from one loop to the next,
        but it can never become shorter (found ids won't dissapear again). This saves us a lot of calculation
        for the display update
        '''
        label_index = 0
        start_of_display_items = cursor_list_pos-self.cursor_row_pos
        print("cursor_list_pos", cursor_list_pos,
              "self.cursor_row_pos", self.cursor_row_pos)
        print("start_of_display_items", start_of_display_items,
              "self.nr_of_rows", self.nr_of_rows)
        for ids_list_index in range(start_of_display_items, min(start_of_display_items + self.nr_of_rows, len(ids_list))):
            label_index = ids_list_index - start_of_display_items+1
            content_index = ids_list[ids_list_index]
            format_telegram = content[content_index]
            print("label_index-start_of_display_items", label_index -
                  start_of_display_items, "self.cursor_row_pos", self.cursor_row_pos)
            print("label_index:", label_index, "content_index",
                  content_index, "text", format_telegram.text)
            if label_index == self.cursor_row_pos + 1:  # +1 is needed because label index starts at 1
                self.labels[label_index].value(
                    format_telegram.text, fgcolor=WHITE, bgcolor=RED)
            else:
                if format_telegram.new:
                    self.labels[label_index].value(
                        format_telegram.text, fgcolor=BLACK, bgcolor=GREEN)
                    format_telegram.new = False
                else:
                    self.labels[label_index].value(
                        format_telegram.text, fgcolor=BLACK, bgcolor=WHITE)

        print("label_index", label_index,
              "self.nr_of_rows", self.nr_of_rows)
        for clear_label in range(label_index+1, self.nr_of_rows+1):
            self.labels[clear_label].value("")
        print("cursor pos", cursor_list_pos, self.last_id)
        for id in ids_list:
            print(id, content[id].text)
        #
        refresh(ssd)

    def show_splash(self):
        self.clear("CANSpy")
        self.labels[self.nr_of_rows//2].value('Scan for Buses')
        refresh(ssd)
