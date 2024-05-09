from cpdui import CPDUI
from espcan import ESPCan
from csmqtt import CSMQTT
from pcbbuttons import KeyPad

print("geht 1")
cpdui=CPDUI()
print("geht 2")
cpdui.draw()
print("geht 3")
can=ESPCan(0.9,10.0)
print("geht 4")
csmqtt=CSMQTT(None)
print("geht 5")
keypad=KeyPad(2)
print("geht 6")
while True:
    can.collect([])
    print(can.telegrams)
    csmqtt.handle_mqtt()
    while keypad.refresh():
        for index, pin in keypad.items():
            print(index,pin.pin, pin.key_up, pin.key_down)



