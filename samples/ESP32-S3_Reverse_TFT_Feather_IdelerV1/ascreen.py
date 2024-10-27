"""
abstract class for all screen related primitives
"""


class AScreen:
    """
    abstract class for all screen related primitives
    """

    def __init__(
        self,
        width: int,
        height: int,
        font_height: int,
        padding: int = 1,
        gap: int = 1,
        marker_width: int = 2,
        orientation: int = 0,
        move_cursor=None,
        back=None,
        select=None,
        eval_mouse_move=None,
    ):
        """
        init
        """
        self.width = width
        self.height = height
        self.orientation = orientation
        self.move_cursor = move_cursor
        self.back = back
        self.select = select
        self.eval_mouse_move = eval_mouse_move
        if orientation == 0 or orientation == 2:
            self.actual_width = width
            self.actual_height = height
        else:
            self.actual_width = height
            self.actual_height = width
        self.font_height = font_height
        self.padding = padding
        self.gap = gap
        self.marker_width = marker_width
        self.mouse_move = False
        self.loop = None
        # calculate some constants
        self.row_height = self.font_height + self.padding + self.gap
        self.frame_x_offset = self.marker_width + 2 * self.gap
        self.text_x_offset = self.frame_x_offset + self.padding
        self.nr_of_rows = self._calculate_nr_of_rows()

    def minmax(self, value, min_value, max_value):
        """
        little helper to adjust a value between min and max
        """
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value

    def lower_first(self, value_1, value_2):
        """
        little helper to make sure that of two values the first one is always the lower one
        """
        if value_1 < value_2:
            return value_1, value_2
        else:
            return value_2, value_1

    def map_mouse_to_grid(self, x: int, y: int):
        """
        calculates, which row have been clicked, and if it was on the left or the right

        returns the screen row  and a boolean for left side

        """
        left = x < self.actual_width / 2
        if y <= self.row_height + self.marker_width:
            return 0, left  # the header
        # remove the header height
        y -= self.marker_width
        y = y // self.row_height
        if y > self.nr_of_rows:
            y = self.nr_of_rows
        return y, left

    def start_mouse_move(self, x: int, y: int):
        """
        stores mouse coords on mouse button down
        """
        self.mouse_move = True
        self.start_mouse_row, self.start_mouse_left = self.map_mouse_to_grid(x, y)

    def stop_mouse_move(self, x: int, y: int):
        """
        calculates the effects when the mouse button is released again
        """
        if self.mouse_move:
            end_x, end_y = x, y
            self.mouse_move = False
            row, left = self.map_mouse_to_grid(x, y)
            # calculate effects
            if self.eval_mouse_move:
                self.eval_mouse_move(
                    self.start_mouse_row, self.start_mouse_left, row, left
                )

    def _calculate_nr_of_rows(self):
        """
        calculates the number of awailable menu rows
        """
        y = self.actual_height
        # first we remove two markers at the top and buttom
        y -= 2 * (self.marker_width + 2 * self.gap)
        total_nr_of_rows = y // self.row_height
        return total_nr_of_rows - 1  # without header

    def text_start(self, row: int):
        """
        calculates the start coordinates for a text of a given row
        """
        if row == 0:  # header
            y = self.padding + self.font_height
        else:
            y = (
                self.padding
                + self.font_height
                + row * self.row_height
                + self.marker_width
                + self.gap
            )
        return self.text_x_offset, y

    def frame_coords(self, row: int):
        """
        calculates the start coordinates for a text of a given row
        """
        if row == 0:  # header
            y1 = 2 * self.padding + self.font_height - self.marker_width
            y2 = 0
        else:
            y1 = (
                # 2 * self.padding
                self.padding
                + self.font_height
                + row * self.row_height
                + self.marker_width
                - self.gap
            )
            y2 = y1 - self.row_height + self.gap
        return (
            self.frame_x_offset,
            y1,
            self.actual_width - self.marker_width - self.gap,
            y2,
        )

    def markers(
        self, back: int, select: int, up: bool, down: bool, select_active, refresh=False
    ):
        """
        paint all markers in one go
        """
        x1, y1, x2, y2 = self.marker_area(False)
        self.draw_rectangle(x1, y1, x2, y2, self.BACKGROUND)
        x1, y1, x2, y2 = self.marker_area(True)
        self.draw_rectangle(x1, y1, x2, y2, self.BACKGROUND)
        if back > -1 and back <= self.nr_of_rows:
            x1, y1, x2, y2 = self.marker_coords(False, back)
            self.draw_rectangle(x1, y1, x2, y2, self.MARKER_BACK)
        if select > -1 and select <= self.nr_of_rows:
            if select_active:
                color = self.MARKER_SELECT
            else:
                color = self.MARKER_INACTIVE

            x1, y1, x2, y2 = self.marker_coords(True, select)
            self.draw_rectangle(x1, y1, x2, y2, color)
        if up:
            color = self.MARKER_UP
        else:
            color = self.BACKGROUND

        x1, y1, x2, y2 = self.marker_up_down_coords(False)
        self.draw_rectangle(x1, y1, x2, y2, color)

        if down:
            color = self.MARKER_DOWN
        else:
            color = self.BACKGROUND

        x1, y1, x2, y2 = self.marker_up_down_coords(True)
        self.draw_rectangle(x1, y1, x2, y2, color)

        if refresh:
            self.refresh()



    def marker_area(self, right_side: bool):
        x1 = 0
        y1 = (
            # 2 * self.padding
            self.padding
            + self.font_height
            + self.nr_of_rows * self.row_height
            + self.marker_width
            - self.gap
        )
        x2 = self.gap + self.marker_width
        y2 = 0
        if right_side:
            x1 += self.actual_width - self.marker_width - self.gap
            x2 += self.actual_width - self.marker_width - self.gap
        return x1, y1, x2, y2

    def marker_coords(self, right_side: bool, row: int):
        """
        calculates the marker coordinates for a text of a given row
        """
        x1 = 0
        x2 = self.marker_width
        if row == 0:  # header
            y1 = 2 * self.padding + self.font_height - self.marker_width
            y2 = 0
        else:
            y1 = (
                # 2 * self.padding
                self.padding
                + self.font_height
                + row * self.row_height
                + self.marker_width
                - self.gap
            )
            y2 = y1 - self.row_height + self.gap
        if right_side:
            x1 += self.actual_width - self.marker_width + 1
            x2 += self.actual_width - self.marker_width
        return x1, y1, x2, y2

    def marker_up_down_coords(self, down: bool):
        """
        calculates the marker coordinates for the up or down marker
        """
        x1 = self.marker_width + self.gap + 1
        x2 = self.actual_width
        x2 -= self.marker_width - self.gap + 2
        y1 = (
            # 2 * self.padding
            self.padding
            + self.font_height
            + self.gap
        )
        if down:
            y1 += self.nr_of_rows * self.row_height + self.marker_width - 1
        y2 = y1 + self.marker_width - 2
        return x1, y1, x2, y2
