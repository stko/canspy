# ESP32-WROOM with SSD1306 OLED

These are two initial tryouts:

The first one (`main.py`) shows detected CAN- IDs, the other one (`webserver.py`) opens its own hotspot, but without further functionality - just tryouts :-)

Just a few notes about the setup:

Micropython Firmware with CAN comes from https://github.com/nos86/micropython/releases (maybe CAN is in the standard distribution some day)

The board is an  MELIFE 0.96" OLED ESP-WROOM-32
* Basd on the wemos lolin32 OLED
* SSD1306 OLED display over I2C on pins 4 (SCL) and 5 (SDA)
* EN does, normally, reset the device
* Display driver: https://github.com/ThingPulse/esp8266-oled-ssd1306
* Flash Mode: Press EN, press Boot shortly, release EN

Flash command

    esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
    esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 /media/ram/esp32-20220117-v1.18.bin 

CAN - Pinout:
| Pin	| Name	| Signal	| Funktion| 
|-------|-------|-----------|---------|
| 22	| GPIO 2	| -	| Display SDA| 
| 24	| GPIO 4	| -	| Display SLC| 
| 25	| GPIO 16	| U2_RXD	| CAN RX| 
| 27	| GPIO 17	| U2_TXD	| CAN TX| 
