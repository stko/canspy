from cpdui import CPDUI
from espcan import ESPCan
from csmqtt import CSMQTT
from pcbbuttons import KeyPad
from lightstrip import LightStrip
import csutils
import json
import microcontroller
import traceback
from pyumenu import UIMenu, Menu, Item


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

uimenu = UIMenu(width=240, height=135,font_size=20)
     
def submenu(row, data=None):
    menu = Menu()
    menu.add_item(Item("submenu", ""))
    menu.add_item(Item("subitem", "1"))
    menu.add_item(Item("another", "2"))
    uimenu.add(menu)


def slider(item, direction, data):
    if direction == "up":
        data[0] += 10
    else:
        data[0] -= 10
    data[0] = item.set_percentage(data[0], str(data[0])+ " %")

   
try:
    status={
        "msgs":{}
    }
    #pdui=CPDUI()
    #cpdui.draw()

    slider_value = [0]
    menu = Menu()
    menu.add_item(Item("Simulation", ""))
    menu.add_item(Item("Temperatur", "27°"))
    menu.add_item(Item("Pressure", "3.4 bar"))
    menu.add_item(Item("Submenu", "-", callback=submenu))
    menu.add_item(Item("Torque", "34 Nm"))
    menu.add_item(Item("Level", "12"))
    menu.add_item(Item("Speed", "17 km/h"))
    menu.add_item(Item("Weight", "88 kg"))
    menu.add_item(Item("Brightness", "70%"))

    percentage_control = Item("Percentage", 0)
    # make an item with to a percentage bar by set an percentage
    percentage_control.set_percentage(10, "10 %")
    menu.add_item(percentage_control)

    # make an item with to a percentage bar by set an percentage
    # and add a callback, which makes it a slider
    slider_control = Item("slider", slider_value[0], callback=slider, data=slider_value)
    slider_control.set_percentage(0)
    menu.add_item(slider_control)

    uimenu.add(menu)


 
    can=ESPCan(0.9,10.0)
    csmqtt=CSMQTT(on_topic)
    keypad=KeyPad(1)
    lightstrip=LightStrip(9)
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
        while keypad.refresh(0.5):
            for index, pin in keypad.items():
                if pin.key_down:
                    print(index,pin.pin, pin.key_up, pin.key_down)
                    if index==keypad.BTN_MENU: # left
                        uimenu.back()
                    elif index == keypad.BTN_SELECT: # right
                        uimenu.select()
                    elif index== keypad.BTN_UP: # up
                        uimenu.move_cursor(-1)
                    elif index==keypad.BTN_DOWN: #down
                        uimenu.move_cursor(1)

except Exception as ex:
    print("reset because of ")
    traceback.print_exception(ex)
    #microcontroller.reset()


