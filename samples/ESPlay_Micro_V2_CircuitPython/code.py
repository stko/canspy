from cpdui import CPDUI
from espcan import ESPCan

print("geht 1")
cpdui=CPDUI()
print("geht 2")
cpdui.draw()
print("geht 3")
can=ESPCan(0.9,10.0)
print("geht 4")

while True:
    can.collect([])
    print(can.telegrams)



