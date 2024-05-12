import json

def load_defaults():
    try:
        with open("offline_defs.json",encoding="utf8") as fin:
            return json.load(fin)
    except:
        return {}

def filter_telegrams(defaults,telegrams):
    result={}
    for module,masks in defaults["modules"].items():
        result[module]={"state":0}
        for id,mask in masks.items():
            id=int(id,16)
            mask=int(mask,16)
            for can_id in telegrams:
                if can_id & mask == id:
                    result[module]["state"]=1
    return result
