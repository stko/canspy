import board
import analogio

class Analogs:
    def __init__(self) -> None:
        self._battery=analogio.AnalogIn(board.A2)
        self._external=analogio.AnalogIn(board.A3)
        self._ignition=analogio.AnalogIn(board.A4)
        self._current=analogio.AnalogIn(board.A5)

    def battery(self):
        return self._battery.value
    
    def external(self):
        return self._external.value
    
    def ignition(self):
        return self._ignition.value
    
    def current(self):
        return self._current.value
    
