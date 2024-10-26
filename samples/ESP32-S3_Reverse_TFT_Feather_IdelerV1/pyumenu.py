"""

pyumenu - show device independed a menu and provides all routines for
nested menus and user selections via bottons, rotary know or touchscreen

"""

from cpscreen import Screen # uncomment for circuitpython with displayio
# from pscreen import Screen  # uncomment for python with tkinter


class Item:
    """
    single menu item
    """

    def __init__(
        self,
        title: str,
        value: str = "",
        callback=None,
        data=None,
    ):
        self.title = title
        self.value = value
        self.slider = False
        self.callback = callback
        self.data = data
        self.percentage = None
        self.menu = None
        self.menu_index = None

    def set_percentage(self, percentage: int, value=None) -> int:
        """
        setting an items percentage makes that item to a slider,
        if also its callback is set
        """
        if percentage > 100:
            percentage = 100
        elif percentage < 0:
            percentage = 0
        if value:
            self.value = value
        if self.callback:
            self.slider = True
        self.percentage = percentage
        ## try to update the screen
        if self.menu and self.menu_index:  # check if parent is set at all
            uimenu = self.menu.uimenu
            if uimenu:
                top_row = self.menu.top_row
                screen_row = self.menu_index - top_row + 1
                if screen_row > 0 and screen_row <= uimenu.screen.nr_of_rows:
                    self.print(uimenu.screen, screen_row, refresh=True)

        return percentage

    def set_parent(self, menu, index):
        self.menu = menu
        self.menu_index = index

    def print(self, screen: Screen, row: int, refresh=False):
        """
        draws the item on the screen
        """
        screen.text(
            row, self.title, self.value, percent=self.percentage, refresh=refresh
        )


class Menu:
    """
    represents a menu containing a list of items

    """

    def __init__(self):
        self.row = 0
        self.top = True
        self.uimenu = None
        self.rows = []
        self.top_row = 1
        self.cursor_row = 1

    def add_item(self, item: Item) -> int:
        """
        adds a new row to the module
        """
        self.rows.append(item)
        index = len(self.rows) - 1
        item.set_parent(self, index)
        return index

    def nr_of_items(self) -> int:
        return len(self.rows) - 1

    def print(self, screen: Screen, row: int, index: int):
        """
        prints item "index" in row "row" on screen
        """
        self.rows[index].print(screen, row)


class UIMenu:
    """

    UIMenu - show device independed a menu and provides all routines for
    nested menus and user selections via bottons, rotary know or touchscreen

    """

    # https://docs.circuitpython.org/projects/miniqr/en/1.3.4/examples.html

    def __init__(self, title="pyUMenu Test", width=320, height=240, font_size=12):
        """
        creates the menu canvas with the given dimensions
        """
        self.screen = Screen(
            title,
            width,
            height,
            padding=10,
            gap=1,
            marker_width=10,
            move_cursor=self.move_cursor,
            back=self.back,
            select=self.select,
            eval_mouse_move=self.eval_mouse_move,
            font_size=font_size,
        )
        self.menus = []
        self.menu = None
        self.slider_active = False

    def authenticate(self, title, abort_text, qrcode, wait_for_authorisation) -> bool:
        """
        a all in one (optional) login screen:
        title: screen header
        abort_text: text of the cancel button. If None, loops forever
        qrcode: the adafruit miniqr qrcode bit matrix
        wait_for_authorisation: callback function. If given, it is called each second to wait
            for authorisation. callback returns True, if authorized
        """
        pass

    def start(self, loop=None):
        """
        starts the event handling of the underlaying graphics interface

        """
        self.screen.start(loop)

    def add(self, menu: Menu):
        """
        adds a new menu structure to the UI. If there's already one shown,
        then the previous one is kept. When then the back() function is called,
        the previous menu is shown again.

        By that a nested menu structure can be realized

        """
        menu.top = len(self.menus) == 0
        self.menus.append(menu)
        self.menu = menu
        menu.uimenu = self
        self._show()

    def _show(self):
        """
        draws the actual menu on the screen

        """
        total_rows = self.menu.nr_of_items()
        for screen_row in range(self.screen.nr_of_rows + 1):
            if screen_row == 0:
                self.menu.print(self.screen, screen_row, 0)
                continue
            if self.menu.top_row + screen_row - 1 > total_rows:
                self.screen.text(screen_row, "", "")
                continue
            self.menu.print(self.screen, screen_row, self.menu.top_row + screen_row - 1)
        self._set_markers()

    def _set_markers(self):
        """
        draws the four color markers for up, down, back and select on the screen
        """
        total_rows = self.menu.nr_of_items()
        actual_item = self._get_actual_item()
        actual_screen_row = (
            self.menu.cursor_row - self.menu.top_row + 1
        )  # in which screen row we are?
        if actual_item.slider:
            back_marker = actual_screen_row
        else:
            back_marker = 0
        top_marker_visible = self.menu.top_row > 1
        is_selectable = actual_item.callback != None or actual_item.slider
        bottom_marker_visible = self.menu.top_row + self.screen.nr_of_rows <= total_rows

        self.screen.markers(
            back_marker,
            actual_screen_row,
            top_marker_visible,
            bottom_marker_visible,
            is_selectable,
            True,
        )

    def _get_actual_item(self):
        return self.menu.rows[self.menu.cursor_row]

    def _adjust_layout(self, force_redraw=False):
        """
        get called after a cursor position change to redraw the screen, if necessary
        """

        redraw_needed = force_redraw
        total_rows = self.menu.nr_of_items()
        if self.menu.cursor_row < self.menu.top_row:  # we moved out of the top
            if self.menu.top_row > 1:  # we need to move the screen topwards
                redraw_needed = True
            self.menu.top_row = self.menu.cursor_row
            if self.menu.top_row < 1:  # did we reached the first item?
                self.menu.top_row = 1
            self.menu.cursor_row = self.menu.top_row
        elif (
            self.menu.cursor_row > self.menu.top_row + total_rows - 1
        ):  # we are over the end of a short list
            self.menu.cursor_row = self.menu.top_row + total_rows - 1
        elif (
            self.menu.cursor_row > self.menu.top_row + self.screen.nr_of_rows - 1
        ):  # we moved out of the bottom
            if (
                self.menu.top_row + self.screen.nr_of_rows <= total_rows
            ):  # we need to move the screen topwards
                redraw_needed = True
            self.menu.top_row = self.menu.cursor_row - self.screen.nr_of_rows + 1
            if (
                self.menu.top_row > total_rows - self.screen.nr_of_rows
            ):  # did we reached the end of the
                self.menu.top_row = total_rows - self.screen.nr_of_rows + 1
            self.menu.cursor_row = self.menu.top_row + self.screen.nr_of_rows - 1

        if redraw_needed:
            self._show()
        else:
            self._set_markers()

    def eval_mouse_move(self, old_row, old_left, row, left):
        """
        redraws the screen depending on the actual mouse movement
        """
        # first the movement
        if row != old_row:  # move it
            move_by = old_row - row
            total_rows = self.menu.nr_of_items()
            self.menu.top_row += move_by
            self.menu.cursor_row = self.menu.top_row + row - 1
            self.menu.top_row = self.screen.minmax(
                self.menu.top_row, 1, total_rows - self.screen.nr_of_rows + 1
            )
            self.menu.cursor_row = self.screen.minmax(
                self.menu.cursor_row, 1, total_rows
            )
            self._adjust_layout(True)
            return
        if row == 0:
            self.back()
            return
        # a item was selected
        # calculate marker position
        self.menu.cursor_row = self.menu.top_row + row - 1
        self.slider_active = False  # moving the cursor leaves the slider mode, if any
        self._adjust_layout()
        actual_item = self._get_actual_item()
        if left and actual_item.slider:
            self.slider_active = True
            self.back()
        else:
            self.select()

    def move_cursor(self, step_width):
        """
        whenever the main application detects an input to change the cursor position
        e.g. by a hardware button or a rotary knob, it calles this function
        to update the UI accourdingly

        """
        self.menu.cursor_row += step_width
        self.slider_active = False  # moving the cursor leaves the slider mode, if any
        self._adjust_layout()

    def select(self, is_rotary_encoder: bool = False):
        """
        whenever the main application detects an input to do the select()
        function e.g. by a hardware button, it calles this function
        to update the UI accourdingly

        if the actual item has a callback- function, this function is called to
        e.g. draw a submenu

        But if the item is a percentage gauge and a callback is set, then
        this makes it to a slider, where the behavior is different:

        When then select() or back() are called, the callback is called
        with a "up" or "down" information to tell the main application to change
        the value. The main application uses then the callback to calculate
        a new value and update the screen by the set_percentage() function
        of that item.

        As so the callback works different, a percentage item can not be a
        submenu item at the same time, and vice versa a submenu item can not
        show a percentage gauge.

        with rotary encoders it's a little bit difficulty, as they have only one knob
        for both menu selection and also slider changes, so we'll need
        the knob button to switch between these both modes


        """
        actual_item = self._get_actual_item()
        if actual_item.slider and not self.slider_active:
            self.slider_active = True
        if self.slider_active:
            if actual_item.callback:
                actual_item.callback(
                    actual_item, "up", actual_item.data
                )  # send a "up" notification to the callback
                return
            return
        if actual_item.callback:
            actual_item.callback(self.menu.cursor_row)  # calls the callback

    def back(self):
        """
        whenever the main application detects an input to do the back()
        function e.g. by a hardware button, it calles this function
        to update the UI accourdingly

        But if the item is a percentage gauge and a callback is set, then
        this makes it to a slider, where the behavior is different:

        When then select() or back() are called, the callback is called
        with a "up" or "down" information to tell the main application to change
        the value. The main application uses then the callback to calculate
        a new value and update the screen by the set_percentage() function
        of that item.

        As so the callback works different, on a slider the back()
        can not jump to a parent menu.

        """
        actual_item = self._get_actual_item()
        if self.slider_active:
            if (
                not actual_item.slider
            ):  # reset slider state just in case it has not properly done before anyhow
                self.slider_active = False
            else:
                if actual_item.callback:
                    actual_item.callback(
                        actual_item, "down", actual_item.data
                    )  # send a "up" notification to the callback
                    return
            return
        if len(self.menus) > 1:  # we are not on the lowest level already..
            self.menus = self.menus[:-1]
            self.menu = self.menus[-1]
            self._show()
