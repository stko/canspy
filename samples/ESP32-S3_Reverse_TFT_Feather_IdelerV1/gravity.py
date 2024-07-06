import time
import board
import busio
import electronutlabs_lis2dh12

class Gravity:
    def __init__(self) -> None:
        # To use default I2C bus (most boards)
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.lis2dh12 = electronutlabs_lis2dh12.LIS2DH12_I2C(i2c, address=0x18)
        self.lis2dh12.range = electronutlabs_lis2dh12.RANGE_2_G

    def acceleration(self):
        # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,
        # z axis values.  Divide them by 9.806 to convert to Gs.
        return [value / electronutlabs_lis2dh12.STANDARD_GRAVITY for value in self.lis2dh12.acceleration]
    
    def gravity(self):
        x,y,z = self.acceleration()
        return [x / 9.806,y / 9.806,z / 9.806]