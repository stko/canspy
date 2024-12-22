Firmware installieren [ESP32-DevKitC-VE-WROVER Download](https://circuitpython.org/board/espressif_esp32_devkitc_v4_wrover/)



Beim Einrichten bei den WLAN- Settings das Passwort vergeben, mit dem später auf 

WLAN Einrichten

http://192.168.1.171/code/ 



Für die Library- Verwaltung `circup` installieren:

```python
python3 -m venv .venv
source .venv/bin/activate
pip install circup [--force]
```

oder die Libraries runterladen von https://circuitpython.org/libraries (die "normalen" Bundles, nicht mit den Communities verwechseln!
Auspacken und in den Device- lib folder kopieren

adafruit_display_text
adafruit_bitmap_font
adafruit_st7789
adafruit_displayio_layout
adafruit_minimqtt
adafruit_connection_manager
adafruit_ticks
adafruit_pcf8574


Die aktuellen Library- Packete
adafruit_ili9341==1.4.2
adafruit_connection_manager==2.0.0
adafruit_bitmap_font==2.1.1
adafruit_display_text==3.1.0
adafruit_display_shapes==2.8.2
adafruit_displayio_layout==None
adafruit_imageload==1.20.2
adafruit_minimqtt==7.6.3



## Connector Pinouts

CAN Bus M12 Female Typ A

| Pin | Signal |
| :-: | :----: |
|  1  |  +BAT  |
|  2  | CAN H  |
|  3  |  GND   |
|  4  | CAN L  |
|  5  |  IGN   |


Sensor Signals M12 Female Typ D

| Pin | Signal |
| :-: | :----: |
|  1  |  +5V   |
|  2  | 1-wire |
|  3  |  GND   |
|  4  |  ADC   |
