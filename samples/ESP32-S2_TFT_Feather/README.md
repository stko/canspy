Buttons

https://www.amazon.de/Clyxgs-Wasserdichte-Momentary-Button-Mikroschalter/dp/B08212J2WY/ref=sr_1_7?adgrpid=71817757195&gclid=Cj0KCQiAxbefBhDfARIsAL4XLRocwXJMym-acWF8omnK_Cn3euxmXhq9ZC3KxT40yvTH7EiGht5zkx4aAj3bEALw_wcB&hvadid=606768452522&hvdev=c&hvlocphy=9043667&hvnetw=g&hvqmt=e&hvrand=7628475258900600392&hvtargid=kwd-370416012847&hydadcr=24874_2308612&keywords=folientaster+wasserdicht&qid=1676560552&sr=8-7

[GitHub - ppelleti/FeatherWing-template-KiCad: A KiCad 5 template for making a FeatherWing board.](https://github.com/ppelleti/FeatherWing-template-KiCad)

Spannungsregler: 

[KICAD quick library generator](http://kicad.rohrbacher.net/quicklib.php)

[LME78_05-1.0: DC - DC-Wandler, 5 W, 5 V, 1000 mA, TO-220 bei reichelt elektronik](https://www.reichelt.de/dc-dc-wandler-5-w-5-v-1000-ma-to-220-lme78-05-1-0-p242853.html?&nbc=1&trstct=lsbght_sldr::242838)

Projektbibliothek:

[Create a Schematic and Symbol Library in KiCad | Sierra Circuits](https://www.protoexpress.com/blog/how-to-create-a-schematic-and-symbol-library-kicad/)

https://www.pcbway.com/blog/PCB_Design_Tutorial/How_to_make_a_footprint_in_KiCad_.html



## Was auf der Platine alles noch fehlt

Überspannungssschutz für den ESP ADC (wie wäre https://forum.arduino.cc/t/best-way-to-protect-analog-input-of-esp32/944669/14 ?)

Überspannungsschutz für den 1-wire Ausgang

Der CAN Tranceiver

Die 5 V Spannungsversorgung, überlebensfähig an einem verstrahlten 24V- Bordnetz

Die Steckpfostenstecker für die folgenden I/O's
1. M12-1 24V in
2. M12-1 GND
3. M12-1 CAN-H
4. M12-1 CAN-L

1. M12-2 5V out
2. M12-2 GND
3. M12-2 ADC in
4. M12-2 1-wire

1. Button Green
2. Button Blue
3. Button Yellow
4. Button Red
5. Button Gnd

Neopixel 3pin SM JST Buchse
1. siehe (nicht vorhandenes) Datenblatt https://technochic.net/blogs/tech-craft-tutorials/neopixel-connectors-connections

