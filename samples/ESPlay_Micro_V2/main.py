from esp32 import CAN
from time import sleep_ms



import esp
esp.osdebug(None)

import gc
gc.collect()


telegrams=[]

bus_valid = False
bus_speeds = [125,250,500]
# reusable buffer to avoid head usage
buf = bytearray(8)
lst = [0, 0, 0, memoryview(buf)]


def scanBus(can, timeout_ms, id=None):
    can.clear_tx_queue()
    can.clear_rx_queue()
    can.send([1,2,3,4,5,6,8], 0x77)
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



# some info about the used can implementation https://github.com/micropython/micropython/pull/7381#issuecomment-931697807

can=None
nr_of_rows=10
last_bus_valid=None
speed_index=len(bus_speeds)
#while True:
for i in range(10):
    if bus_valid == False:
        if last_bus_valid != bus_valid:
            telegrams.clear()
        last_bus_valid= bus_valid
        speed_index +=1
        if speed_index>=len(bus_speeds):
            speed_index=0
        if can:
            can.deinit()
        print("scan {}kb".format(bus_speeds[speed_index]))

        
        can = CAN(0,
            mode=CAN.NORMAL,
            #mode=CAN.SILENT,
            # because of a bug in the espressif library the actual baudrate need to multiplied by 2
            baudrate=250000,
            #baudrate=bus_speeds[speed_index] * 1000,
            # esplay SDA=IO21 = tx, SCL=IO22 = rx
            tx=21,
            rx=22
        )

        bus_valid=scanBus(can, 1000)

    else:
        if last_bus_valid != bus_valid:
            print("Bus found {}kb".format(bus_speeds[speed_index]))
        last_bus_valid= bus_valid
        bus_valid=scanBus(can, 1000)
    if bus_valid:
        print("Bus {} kB ok".format(bus_speeds[speed_index]))
        telegram_lines=len(telegrams)
        # to avoid memory run out, we limit the number of stored telegrams

        telegrams=telegrams[-10:]
        for line_count in range (min(nr_of_rows,len(telegrams))):
            id = telegrams[line_count]["id"]
            data = telegrams[line_count]["data"]
            print("{:04x}".format(id).upper() + " " + "".join(["{:02x}".format(x) for x in data[:6]]).upper())

can.info()                  # get information about the controller’s error states and TX and RX buffers
can.deinit()                # turn off the can bus
can.clear_rx_queue()        # clear messages in the FIFO
can.clear_tx_queue()        # clear messages in the transmit buffer            
gc.collect()

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