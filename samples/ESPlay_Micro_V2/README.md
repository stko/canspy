# CANSpy auf einem ESPlay Micro V2

## Setup 
Unter Unbuntu 22.04 wird der ch341-uart des ESPLay dummerweise für ein Braille- Device gehalten, und weil das Braille- Device dann nicht richtig initialiert werden kann, wirft der Braille- Treiber das ganze ttyUSB0- Device wieder raus 

Abhilfe für Ubuntu 22.04:
  sudo apt remove brltty



## Reparieren des Bootloaders

Wenn sich aus unerfindlichen Gründen der Bootloader verabschiedet haben soll, kann man ihn glücklicherweise durch Neuflashen wieder herstellen - Schwein gehabt! https://github.com/pebri86/esplay-base-firmware/releases/tag/v1.0-esplay-micro

## Boot-Image selbst gebaut

In Verzeichnis `make_fw` ist beschrieben, wie man sich eigene Boot- Images bauen kann.

Die fertigen Firmware- Images *.fw (selbstgemacht oder fertig) gehören dann auf der SD-Karte ins  `/esplay/firmware`- Verzeichnis, um vom Bootloader gefunden zu werden. Fertige Images gibts auch auf https://github.com/pebri86/esplay-micro-firmware-collections

