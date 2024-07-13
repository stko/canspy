from cpdui import CPDUI
from espcan import ESPCan
from csmqtt import CSMQTT
from pcbbuttons import KeyPad
from lightstrip import LightStrip
import csutils
import json
import microcontroller
import traceback

ignition_pin=None

def on_topic(data):
    global defaults,ignition_pin
    try:
        print("mqtt string",data)
        data=json.loads(str(data))
        if "modules" in data:
            defaults["modules"]=data["modules"]
        if "ignition" in data and ignition_pin:
            ignition_pin.value=data["ignition"]
    except Exception as ex:
        print("JSON error", ex,data)
try:
    status={
        "msgs":{}
    }
    cpdui=CPDUI()
    cpdui.draw()
    can=ESPCan(0.9,10.0)
    csmqtt=CSMQTT(on_topic)
    keypad=KeyPad(1)
    lightstrip=LightStrip()
    ignition_pin=keypad.get_pin(5)
    ignition_pin.switch_to_output(value=False)
    defaults=csutils.load_defaults()
    while True:
        can.collect([])
        print(can.telegrams)
        lightstrip.set_status(3)
        status["msgs"]=csutils.filter_telegrams(defaults,can.telegrams)
        print("modules")
        for module,data in status["msgs"].items():
            print(module, data["state"])
        csmqtt.send_topic({"can": can.telegrams,"sensors":csutils.collect_sensors()})
        csmqtt.handle_mqtt()
        #keypad.refresh() 
        while keypad.refresh():
            for index, pin in keypad.items():
                print(index,pin.pin, pin.key_up, pin.key_down)
except Exception as ex:
    print("reset because of ")
    traceback.print_exception(ex)
    #microcontroller.reset()


