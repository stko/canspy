# CANSpy auf einem ESPlay Micro V2

## Setup 
Unter Unbuntu 22.04 wird der ch341-uart des ESPLay dummerweise für ein Braille- Device gehalten, und weil das Braille- Device dann nicht richtig initialiert werden kann, wirft der Braille- Treiber das ganze ttyUSB0- Device wieder raus 

Abhilfe für Ubuntu 22.04:
  sudo apt remove brltty


## Flashing the micropython image
As of status of today, CAN is not included in the offical micropython ESP32 port, we are using
a development version (Many hanks to https://github.com/micropython/micropython/pull/9532#issuecomment-1308504791 !)

Download and unzip [2022.10.06.zip](https://github.com/micropython/micropython/files/9969695/2022.10.06.zip)

flash it 

  esptool.py -p /dev/ttyUSB0 -b 460800 --before default_reset --after hard_reset --chip esp32  write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin


## Installation of the Graphics Driver
CANSpy is using the nano-gui micropython graphics library, which is available for a brought range of systems. When using it, it needs a little bit of setup and configuration, which is explained here for the ESPlay Micro 2 and its 2,4" ILI9341 TFT Panel. Other displays on other systems would be simular.

Get a copy of the latest driver

    git clone --depth=1 https://github.com/peterhinch/micropython-nano-gui
    

Delete all unused files and dirs, keep just the driver and the gui directory

    rm -vr !("drivers"|"gui")
    cd drivers
    rm -vr !("ili93xx"|"boolpalette.py")
    cd ..





install the `rshell` tool

    pip3 install rshell

start `rshell` and connect to the board

    connect serial /dev/ttyUSB0

verify your found board name

    boards

transfer the gui files - here the board name was shown as `pyboard` in the `boards` command

    cp -r drivers /pyboard
    cp -r gui /pyboard
    cp color_setup.py /pyboard

then change the directory to where this CANSpy repository is located and copy the CANSpy files

    cp main.py /pyboard


enter the `repl`

    repl

and fire the graphic demo

    import gui.demos.aclock
    




## Create own firmware packages for the ESPlay

Attention: This is *not* needed for the CANSpy today!- this is just the documentation of the trial
to make the firmware exchangeable, which failed for now, so the todays micropython is
hard burned into the device, but maybe we get his fixed in the future...

### Repair the ESPLay Bootloader

In case the original bootloader is destroyed (eg. by using micropython...), it can be repaired
following the instructions on https://github.com/pebri86/esplay-base-firmware/releases/tag/v1.0-esplay-micro

### Create an own boot image

The directory mkfw contains the howto of how make an image out of a firmware, which can be then selected
from SD-Card and flashed by the ESPlay Bootloader

