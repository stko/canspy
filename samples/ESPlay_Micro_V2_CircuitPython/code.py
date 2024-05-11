from cpdui import CPDUI
from espcan import ESPCan
from csmqtt import CSMQTT
from pcbbuttons import KeyPad
import csutils
status={
    "msgs":{}
}
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
defaults=csutils.load_defaults()
while True:
    can.collect([])
    print(can.telegrams)
    status["msgs"]=csutils.filter_telegrams(defaults,can.telegrams)
    print("modules")
    for module,data in status["msgs"].items():
        print(module, data["state"])
    csmqtt.send_topic(can.telegrams)
    csmqtt.handle_mqtt()
    while keypad.refresh():
        for index, pin in keypad.items():
            print(index,pin.pin, pin.key_up, pin.key_down)



