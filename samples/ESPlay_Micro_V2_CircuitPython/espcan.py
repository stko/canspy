'''
espcan - autodetect the frame speed, listen for filtered messages and send telegrams

'''
import canio
import time
import board
import binascii

class ESPCan:
    def __init__(self, timeout: float, store_time: float, forced_baudrate: int = 0):
        '''
        if forced_bautrate is given, the bus speed scan is skipped and the transceiver
        goes straight in active with the given baud_rate
        Otherways the module must receive first some foreign telegram in silent mode to syncronise 
        to the found bus speed and goes into active
        '''


        # If the CAN transceiver has a standby pin, bring it out of standby mode
        if hasattr(board, 'CAN_STANDBY'):
            standby = digitalio.DigitalInOut(board.CAN_STANDBY)
            standby.switch_to_output(False)
        
        # If the CAN transceiver is powered by a boost converter, turn on its supply
        if hasattr(board, 'BOOST_ENABLE'):
            boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
            boost_enable.switch_to_output(True)


        self.telegrams={}
    
        self.bus_valid = False
        self.last_bus_valid=False
        self.bus_speeds = [125_000,250_000,500_000]
        self.speed_index=len(self.bus_speeds)-1
        self.timeout=timeout
        self.store_time=store_time
        self.can=None
        self.fixed_baudrate = (forced_baudrate >0)
        self.baudrate = forced_baudrate # shall contain the actual baud rate. 0 when bus is not identified yet
        if self.baudrate:
            self.open_can_device(self.baudrate,False) # open can straight in NORMAL mode

    def open_can_device(self, baudrate: int,bus_silent= True):
        if self.can:
            self.can.deinit()
        # Use this line if your board has dedicated CAN pins. (Feather M4 CAN and Feather STM32F405)
        # self.can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=250_000, auto_restart=True)
        # On ESP32S2 most pins can be used for CAN.  Uncomment the following line to use IO5 and IO6
        self.can = canio.CAN(rx=board.IO14, tx=board.IO15, baudrate=baudrate, silent=bus_silent, auto_restart=True)
        # according to the docs the listener creation is very extensive, so we do it just always when we reconfigure the bus
        self.listener = self.can.listen( timeout=self.timeout)



    def scan_bus(self) -> bool : # returns true if something receiced
        '''
        listen on the bus and fills the telegrams buffer with all last received msgs, one per id
        '''
        #print("scan")
        start_time = time.monotonic()
        expired_time = start_time -self.store_time
        # delete old messages first
        to_delete=[]
        for id, data in self.telegrams.items():
            if data["t"]<expired_time:
                to_delete.append(id)
        for id in to_delete:
            del(self.telegrams[id])
        success=False
        for message in self.listener:
            if not message:
                break
            recv_time=time.monotonic()
            #print(recv_time,self.timeout,start_time)
            if recv_time-self.timeout > start_time:
                break
            # as we might miss some message, we store them for a while as a buffer 
            self.telegrams[message.id]= {"t": recv_time, "msg":binascii.hexlify(message.data)}
            success=True
        return success

    def collect(self, id_list) -> bool : # returns true if something receiced
        success=False
        if self.fixed_baudrate: # we don't want to change
            success= self.scan_bus()
        else:
            if self.baudrate: # we have 
                success=self.scan_bus()
                if not success:
                    self.baudrate=0
            if not self.baudrate:
                self.speed_index +=1
                if self.speed_index>=len(self.bus_speeds):
                    self.speed_index=0
                print("Try can speed", self.bus_speeds[self.speed_index])
                self.open_can_device(self.bus_speeds[self.speed_index])
                success=self.scan_bus()
                if success:
                    self.baudrate=self.bus_speeds[self.speed_index]
                    self.open_can_device(self.bus_speeds[self.speed_index],False) # re-open can in NORMAL mode
        return success

