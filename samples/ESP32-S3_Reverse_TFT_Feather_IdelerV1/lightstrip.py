import board
import neopixel

class LightStrip:
    def __init__(self) -> None:
        """
        self.pixels = neopixel.NeoPixel(board.D12, 9, auto_write=False)
        self.pixels[0] = (255, 255, 255)
        self.pixels[8] = (255, 45, 0)
        self.pixels.show()
        """
        self.pixels = neopixel.NeoPixel(board.D12, 9)


    def set_status(self, state:int):
        '''
        self.pixels[0] = (255, 255, 255)
        self.pixels[8] = (255, 45, 0)
        self.pixels.show()
        '''
        self.pixels.fill(0xADAF00)
