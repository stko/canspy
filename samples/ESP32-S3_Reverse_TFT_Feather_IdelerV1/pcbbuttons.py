
import adafruit_pcf8574
import board
import digitalio
import time

class KeyHandle:
    '''
    parent class for different types of button inputs
    '''
    def __init__(self, inverted=False):
        self.is_inverted= inverted
        self._pin = self.get_pin()
        
        self.old_value = False
        self.is_pressed = False  # the only static value: its True if the key is actual pressed
        # an event flag: its True in the moment where the key is just gone through a down/up sequence
        self.was_pressed = False
        # an event flag: its True in the moment where the key was just pressed
        self.key_down = False
        self.key_up = False  # an event flag: its True in the moment where the key was just released
        self.debounce = 0
        self.last_key_event_time=0


    def get_pin(self) -> bool:
        '''
        this is a generic routine made for digial standard pins

        this routine needs to be overwitten for the different implementation


        the returned value must be True if the button is pressed

        '''

        return False # we won't need this for PCF8574

    @property
    def pin(self):
        return self.get_pin()


    def refresh(self, debounce) -> bool:
        '''
        returns true if any input change has found
        '''
        any_change=False
        actual_state=self.get_pin()
        if not actual_state and self.debounce > 0:
            self.debounce -= 1
        if actual_state and self.debounce < 2 * debounce:
            self.debounce += 1
        debounced_state = self.debounce >= debounce
        self.is_pressed=debounced_state
        if self.old_value is not debounced_state:
            any_change= True
            if debounced_state:
                self.key_up=False
                self.key_down=True
            else:
                self.key_up=True
                self.key_down=False
        else:
            self.key_down=False
            self.key_up=False
        self.old_value=debounced_state
        return any_change
            
class PinKeyHandle(KeyHandle):
    def __init__(self, board_pin,pull=None,inverted=False):
        self.board_pin=digitalio.DigitalInOut(board_pin)
        self.board_pin.switch_to_input(pull=pull)
        super().__init__(inverted)
        self.pin = self.get_pin()
        

    def get_pin(self):
        '''
        this is for digial standard pins
        '''

        #that's the command for norml GPIOs
        return self.board_pin.value == 1 ^ self.is_inverted


class PCFKeyHandle(KeyHandle):
    def __init__(self, pcf__pin,inverted=False):
        self.board_pin=pcf__pin
        self.board_pin.switch_to_input(digitalio.Pull.UP)
        super().__init__(inverted)
        self._pin = self.get_pin()
        self.last_key_event_time=0


    def get_pin(self):
        '''
        this routine overrides the generic routine with the pcf sprecific function
        '''
        return self.board_pin.value == 1 ^ self.is_inverted

    @property
    def pin(self):
        return self.get_pin()



class KeyPad(dict):
    BTN_LEFT=const(0) 
    BTN_RIGHT=const(1) 
    BTN_UP=const(2)
    BTN_DOWN=const(3) 
    BTN_SELECT=const(4)
    BTN_MENU=const(5)
    BTN_L=const(6)
    BTN_R=const(7)

    def __init__(self, debounce, inverted=False):
        super().__init__()
        # To use default I2C bus (most boards)
        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

        # To create I2C bus on specific pins
        import busio

        self.pcf = adafruit_pcf8574.PCF8574(i2c)
        self.debounce=debounce
        self.last_key_event_time=0
        # create instances for all inputs
        self[self.BTN_LEFT]=KeyHandle() # unused

        self[self.BTN_RIGHT]=KeyHandle() # unused
        self[self.BTN_UP]=PCFKeyHandle(self.pcf.get_pin(1),inverted) # green
        self[self.BTN_DOWN]=PCFKeyHandle(self.pcf.get_pin(3),inverted) # yellow
        self[self.BTN_SELECT]=PCFKeyHandle(self.pcf.get_pin(2),inverted) # red
        self[self.BTN_MENU]=PCFKeyHandle(self.pcf.get_pin(0),inverted) # blue
        self[self.BTN_L]=KeyHandle() # unused
        self[self.BTN_R]=KeyHandle() # unused

    
    def refresh(self,wait_time:float) -> bool:
        '''
        refreshes the state of all keys

        this is done here at a single place to have a common debounce behaviour for all keys

        returns True if any input change has been detected  or if last key pressed is within the debouce time
        '''
        any_change=False
        this_time=time.monotonic()
        for id, key in self.items():
            this_change=key.refresh(self.debounce)
            if this_change:
                print("key change",id,this_change)
                self.last_key_event_time=this_time
                any_change = True
        return any_change or self.last_key_event_time + wait_time> this_time

    def get_pin(self,pin_nr)-> board.DigitalInOut:
        return self.pcf.get_pin(pin_nr)
            


