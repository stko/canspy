from micropython import const

#import pcf8574
from machine import I2C, Pin


class KeyHandle:
    def __init__(self, pin_nr):
        self.is_inverted= pin_nr <0
        pin_nr=abs(pin_nr)
        self.pin_nr=pin_nr
        self.pin = self.get_pin(pin_nr)
        
        self.old_value = False
        self.is_pressed = False  # the only static value: its True if the key is actual pressed
        # an event flag: its True in the moment where the key is just gone through a down/up sequence
        self.was_pressed = False
        # an event flag: its True in the moment where the key was just pressed
        self.key_down = False
        self.key_up = False  # an event flag: its True in the moment where the key was just released
        self.debounce = 0

        '''# PCF8574  & ESPlay specific
        i2c = I2C(scl=Pin(22), sda=Pin(21))
        pcf = pcf8574.PCF8574(i2c, 0x20)
        '''

    def get_pin(self,pin_nr):
        '''
        this is a generic routine made for digial standard pins

        this routine needs to be overwitten in case of any non standard pins!


        the returned value must be an object with a method "value" which returns 1 is the button is pressed

        '''

        #that's the command for norml GPIOs
        return Pin(self.pin_nr, Pin.IN)
        #return None # we won't need this for PCF8574

    def get_pin_state(self):
        # that is for normal GPIO -Pins
        return self.pin.value() == 1 ^self.is_inverted
        #self.pcf.pin(self.pin_nr)


    def refresh(self, debounce):
        actual_state = self.get_pin_state()
        print(actual_state)
        if not actual_state and self.debounce > 0:
            self.debounce -= 1
        if actual_state and self.debounce < 2 * debounce:
            self.debounce += 1
        debounced_state = self.debounce >= debounce
        self.is_pressed=debounced_state
        if self.old_value is not debounced_state:
            if debounced_state:
                self.key_up=False
                self.key_down=True
            else:
                self.key_up=True
                self.key_down=False
        else:
            self.key_down=False
            self.key_up=False

class KeyPad(dict):
    BTN_LEFT=const(0) 
    BTN_RIGHT=const(1) 
    BTN_UP=const(2)
    BTN_DOWN=const(3) 
    BTN_SELECT=const(4)
    BTN_MENU=const(5)
    BTN_L=const(6)
    BTN_R=const(7)

    def __init__(self, debounce):
        super().__init__()
        self.debounce=debounce
        # here we mal our virtual button IDs against the real pin IDs
        map_pins={
            0:0,    #left -unused
            1:0,    #right  -unused
            2:-34,   # up -mapped on Button R_BTN
            3:0,   #down   -unused
            4:0,   # Select -unused
            5:-35,    #Menu 
            6:0,    #L -unused
            7:0,    #R -unused
            }
        for btn in [ self.BTN_UP,self.BTN_MENU]:
            self[btn]=KeyHandle(map_pins[btn])
    
    def refresh(self):
        '''
        refreshes the state of all keys

        this is done here at a single place to have a common debounce behaviour for all keys
        '''

        for key in self.values():
            key.refresh(self.debounce)

            
