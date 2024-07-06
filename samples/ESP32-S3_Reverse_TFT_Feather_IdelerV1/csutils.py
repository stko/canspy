import json
from gravity import Gravity
from analogs import Analogs

def load_defaults():
    try:
        with open("offline_defs.json",encoding="utf8") as fin:
            return json.load(fin)
    except:
        return {}

def filter_telegrams(defaults,telegrams):
    result={}
    for module,settings in defaults["modules"].items():
        result[module]={"state":0}
        for id,mask in settings["msgs"].items():
            id=int(id,16)
            mask=int(mask,16)
            for can_id in telegrams:
                if can_id & mask == id:
                    result[module]["state"]=1
    return result

gravity=Gravity()
analogs=Analogs()


def collect_sensors():
    return {
        "battery":analogs.battery(),
        "external":analogs.external(),
        "ignition":analogs.ignition(),
        "current":analogs.current(),
        "temp":34.3,
        "gx":gravity.acceleration()
        }
