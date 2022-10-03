from machine import I2C, Pin, CAN
from ssd1306 import SSD1306_I2C
from time import sleep_ms
import micropython

# Display driver from https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py

# https://github.com/hmaerki/micropython/tree/master/canbus_example

# https://github.com/nos86/micropython/blob/esp32-can-driver/examples/esp32_can.py
# https://github.com/nos86/micropython/blob/esp32-can-driver/docs/library/machine.CAN.rst

import esp
esp.osdebug(None)

import gc
gc.collect()


# Initialisiere den I2C-Bus
bus = I2C(scl=Pin(4), sda=Pin(2))
#bus = SoftI2C(Pin(4), Pin(2))

# Initialize the display

x_size=128
y_size=64

nr_of_rows=7 
oled = SSD1306_I2C(x_size, y_size, bus)
oled.fill(0)

telegrams=[]

bus_valid = False
bus_speeds = [125,250,500]
# reusable buffer to avoid head usage
buf = bytearray(8)
lst = [0, 0, 0, memoryview(buf)]

def framebuffer_print(row, text,color=1):
    hx=8
    hy=hx
    oled.text(text, 0, row*hy,color)
    '''
    for col in range(int(x_size/hx)):
        for row in range(int(y_size/hy)):
            oled.text("A", col*hx, row*hy)
    '''
def framebuffer_clear():
    oled.fill(0)
    
def framebuffer_show():
    oled.show()    

def draw_init_screen():
    framebuffer_clear()
    framebuffer_print(1," MT Technology")
    framebuffer_print(3,"   CAN SPY")
    framebuffer_print(5," Search Bus...")
    framebuffer_show()

    

def scanBus(can, timeout_ms, id=None):
    #can.clear_tx_queue()
    can.clear_rx_queue()
    if id:
        can.setfilter(0, CAN.FILTER_ADDRESS, [id, 0])
    #can.send([1,2,3,4,5,6,8], id)
    sleep_ms(timeout_ms)
    if can.any() == True:
        while can.any() == True:
            r=can.recv()
            id=r[0]
            data=r[3]
            telegrams.append({"id":id , "data":data})
        return True
    else:
        return False



can=None
last_bus_valid=None
speed_index=len(bus_speeds)
while True:
#for i in range(10):
    if bus_valid == False:
        if last_bus_valid != bus_valid:
            draw_init_screen()
            telegrams.clear()
        last_bus_valid= bus_valid
        speed_index +=1
        if speed_index>=len(bus_speeds):
            speed_index=0
        if can:
            can.deinit()
        #print("scan {}kb".format(bus_speeds[speed_index]))
        can = CAN(0,
                  extframe=False,
                  #mode=CAN.SILENT_LOOPBACK,
                  mode=CAN.SILENT,
                  #mode=CAN.NORMAL,
                  # baudrate=CAN.BAUDRATE_500k,
                  baudrate=bus_speeds[speed_index],
                  # rx2/tx2
                  tx_io=17, rx_io=16, auto_restart=False)
        bus_valid=scanBus(can, 1000)

    else:
        if last_bus_valid != bus_valid:
            print("Bus found {}kb".format(bus_speeds[speed_index]))
        last_bus_valid= bus_valid
        bus_valid=scanBus(can, 1000)
    if bus_valid:
        framebuffer_clear()
        framebuffer_print(1,"Bus {} kB ok".format(bus_speeds[speed_index]),1)
        telegram_lines=len(telegrams)
        # to avoid memory run out, we limit the number of stored telegrams
        '''
        entries_to_remove = list(telegrams.keys())[10:]
        for k in entries_to_remove:
            telegrams.pop(k, None)
        if telegram_lines> nr_of_rows:
            telegram_lines=nr_of_rows
        for id,data in telegrams.items():
            if telegram_lines<3:
                break
            framebuffer_print(telegram_lines, "{:04x}".format(id).upper() + " " + "".join(["{:02x}".format(x) for x in data[:6]]).upper(),3)
            telegram_lines-=1
        '''
        telegrams=telegrams[-10:]
        for line_count in range (min(nr_of_rows,len(telegrams))):
            id = telegrams[line_count]["id"]
            data = telegrams[line_count]["data"]
            framebuffer_print(line_count +2, "{:04x}".format(id).upper() + " " + "".join(["{:02x}".format(x) for x in data[:6]]).upper(),3)
        framebuffer_show()


'''

kept it here, maybe we'll need it somewhere later

def sendAndCheck(can, name, id, expectedLP=True):
    can.clear_tx_queue()
    can.clear_rx_queue()
    can.send([1,2,3,4,5,6,8], id)
    sleep_ms(100)
    if can.any() == expectedLP:
        print("{}: OK".format(name))
        if expectedLP:
            r=can.recv()
            print("Bla",r)
    else:
        print("{}: FAILED".format(name))



# Test send/receive message
print("Loopback Test: no filter - STD")
sendAndCheck(can, "No filter", 0x100, True)

# Set filter1
print("Loopback Test: one filter - STD")
can.setfilter(0, CAN.FILTER_ADDRESS, [0x101, 0])
sendAndCheck(can, "Passing Message", 0x101, True)
sendAndCheck(can, "Blocked Message", 0x100, False)

# Set filter2
print("Loopback Test: second filter - STD")
can.setfilter(0, CAN.FILTER_ADDRESS, [0x102, 0])
sendAndCheck(can, "Passing Message - Bank 1", 0x102, True)
sendAndCheck(can, "Passing Message - Bank 0", 0x101, True)
sendAndCheck(can, "Blocked Message", 0x100, False)

# Remove filter
print("Loopback Test: clear filter - STD")
can.clearfilter()
sendAndCheck(can, "Passing Message - Bank 1", 0x102, True)
sendAndCheck(can, "Passing Message - Bank 0", 0x101, True)
sendAndCheck(can, "Passing any Message", 0x100, True)
'''

#oled.poweroff()