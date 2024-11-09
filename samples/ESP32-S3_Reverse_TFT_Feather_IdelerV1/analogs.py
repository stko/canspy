import board
import analogio
from adafruit_onewire.bus import OneWireBus
import adafruit_ds18x20
class Analogs:
    def __init__(self) -> None:
        self._battery=analogio.AnalogIn(board.A2)
        self._external=analogio.AnalogIn(board.A3)
        self._ignition=analogio.AnalogIn(board.A4)
        self._current=analogio.AnalogIn(board.A5)
        self.ow_bus = OneWireBus(board.D13)
        print("Resetting bus...", end="")
        if self.ow_bus.reset():
            print("OK.")
        else:
            print("Nothing found on bus.")

        # Run a scan to get all of the device ROM values
        print("Scanning for devices...", end="")
        self.devices = self.ow_bus.scan()
        print("OK.")
        print("Found {} device(s).".format(len(self.devices)))
        # For each device found, print out some info
        for i, d in enumerate(self.devices):
            print("Device {:>3}".format(i))
            print("\tSerial Number = ", end="")
            for byte in d.serial_number:
                print("0x{:02x} ".format(byte), end="")
            print("\n\tFamily = 0x{:02x}".format(d.family_code))
        self.ds18b20 = None
        if self.devices:
            self.ds18b20 = adafruit_ds18x20.DS18X20(self.ow_bus, self.devices[0])
            print('Temperature: {0:0.3f} °C'.format(self.ds18b20.temperature))

    def battery(self):
        return self._battery.value
    
    def external(self):
        return self._external.value
    
    def ignition(self):
        return self._ignition.value
    
    def current(self):
        return self._current.value    

    def temperature(self):
        if self.ds18b20:
            return self.ds18b20.temperature
        return 0.0
    
