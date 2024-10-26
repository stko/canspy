import time
import board
import neopixel

class LightStrip:
    def __init__(self, nr_of_leds: int) -> None:
        self.nr_of_leds = nr_of_leds
        self.offset = 0
        self.pixels = neopixel.NeoPixel(board.D12, nr_of_leds, auto_write=False)
        self.pixels[0] = (255, 255, 255)
        self.pixels[8] = (255, 45, 0)
        self.pixels.show()
        # self.pixels = neopixel.NeoPixel(board.D12, 9)

    def set_status(self, state: int):
        self.offset += 1
        color = (16, 8, 0)
        if self.offset >= self.nr_of_leds:
            self.offset = 0
        for looper in range(self.nr_of_leds):
            for index in range(self.nr_of_leds):
                if index == looper:
                    self.pixels[index] = tuple(
                        {idx: value // 2 for idx, value in enumerate(color)}
                    )
                else:
                    self.pixels[index] = color
            self.pixels.show()
            time.sleep(0.05)
        self.pixels[self.nr_of_leds - 1] = color
        self.pixels.show()
        # self.pixels.fill(0x00AFAF)
