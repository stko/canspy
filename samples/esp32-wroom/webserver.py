from machine import I2C, Pin, CAN
from ssd1306 import SSD1306_I2C
from time import sleep_ms
import micropython
# Display driver from https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
# Web server : https://github.com/jczic/MicroWebSrv
# https://github.com/hmaerki/micropython/tree/master/canbus_example
# https://github.com/nos86/micropython/blob/esp32-can-driver/examples/esp32_can.py
# https://github.com/nos86/micropython/blob/esp32-can-driver/docs/library/machine.CAN.rst
# Access point https://randomnerdtutorials.com/micropython-esp32-esp8266-access-point-ap/
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
ssid = 'CAN-Spy'
password = 'canspy'
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)
while ap.active() == False:
  pass
# Web server : https://github.com/jczic/MicroWebSrv
#@MicroWebSrv.route('/show/<level>/<id>')
from microWebSrv import MicroWebSrv
@MicroWebSrv.route('/show/<level>/<id>')
def handlerFuncEdit(httpClient, httpResponse, routeArgs) :
  print("In EDIT HTTP variable route :")
  wait_for_connect=False
  content   = """\ 
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="UTF-8" />
      <title>EDIT CAN SPY</title>
    </head>
    <body>
      <h1>K&ouml;hlers ESP32 Hotspot</h1>
      geht doch...<br />
      level : %d<br />
      id : %d<br />
    </body>
  </html>
  """ % ( routeArgs["level"],
          routeArgs["id"] )
  httpResponse.WriteResponseOk( headers         = None,
                                contentType     = "text/html",
                                contentCharset  = "UTF-8",
                                content         = content )
mws = MicroWebSrv()      # TCP port 80 and files in /flash/www
mws.Start(threaded=True) # Starts server in a new thread
wait_for_connect=True
print("Runs..")
def my_handler_mainloop(reason):
  (id, isRTR, filterMatchIndex, telegram) = can.recv(0)
  print("received:", telegram)
def my_canbus_interrupt(bus, reason):
  # Don't handle code in the interrupt service routine.
  # Schedule a task to be handled soon
  if reason == 0:
    # print('pending')
    micropython.schedule(my_handler_mainloop, reason)
    return
  if reason == 1:
    print('full')
    return
  if reason == 2:
    print('overflow')
    return
  print('unknown')
#can.rxcallback(0, my_canbus_interrupt)
# Initialisiere den I2C-Bus
bus = I2C(scl=Pin(4), sda=Pin(2))
#bus = SoftI2C(Pin(4), Pin(2))
x_size=128
y_size=64
oled = SSD1306_I2C(x_size, y_size, bus)
hx=8
hy=hx
oled.fill(0)
for col in range(int(x_size/hx)):
    for row in range(int(y_size/hy)):
        oled.text("W", col*hx, row*hy)
oled.show()
while wait_for_connect:
  sleep_ms(500)
#oled.poweroff()
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
can = CAN(0,
          extframe=False,
          #mode=CAN.SILENT_LOOPBACK,
          mode=CAN.NORMAL,
          # baudrate=CAN.BAUDRATE_500k,
          baudrate=500,
          # rx2/tx2
          tx_io=17, rx_io=16, auto_restart=False)
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
oled.poweroff()