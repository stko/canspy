## Boot-Image selbst gebaut

Dies ist hier für den ESPLay Micro V2 beschrieben, bei anderen Geräten wird der Prozess anders sein...

Zuerst einmal braucht man das tool, was das fertige Image packt. Das Programm in `mkfw` ist eine modifizerte Version des Originals von https://github.com/pebri86/esplay-base-firmware/tree/master/tools mit zusätzlicher Eingabe der Firmware-Eingabedatei. 



Dann besorgt man sich das gewünschte Bildchen, was in der Firmware- Übersicht angezeigt werden soll und sorgt dafür, dass es als PNG- Datei mit den Abmessungen 86 * 48 vorliegt. Gespeichert wird das Bild im Verzeichnis `inputs` als `ImageName`.png.

Ebenso speichert man die ursprüngliche Firmware-Datei, welches ins fertige Image übertragen werden soll, als `ImageName`.bin ebenfalls im `inputs`- Verzeichnis.

Dann ruft man das `make_fs.sh` Script auf mit dem Namen des gewünschten Images "`Imagename`" und dem kurzen Text, der im Bootloader mit angezeigt werden soll, und zwar in Hochkommatas, also

    make_fs.sh ImageName "Meine Beschreibung"

Danach findet sich das fertige Boot-Image unter dem Namen `ImageName` im Verzeichnis `build`


