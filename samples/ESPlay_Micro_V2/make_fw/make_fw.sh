#!/bin/bash

CONVERTER="mkfw/mkfw"
TARGETDIR="build"

INPUTIMAGE="inputs/$1.bin"
TILEINPUTFILE="inputs/$1.png"
TILEFILE="inputs/$1.raw"
DESCR="$2"

if [  -z "$DESCR" ]; then
    DESCR="$1"
fi
if [ ! -f "$INPUTIMAGE" ]; then
    echo "Error: Firmware input file $INPUTIMAGE does not exist- Exit"
    exit 1
fi
if [ ! -f "$TILEINPUTFILE" ]; then
    echo "Error: Picture input file $TILEINPUTFILE does not exist- Exit"
    exit 1
fi
( cd mkfw && make )
if [ ! -f "$CONVERTER" ]; then
    echo "Error: Image converter $CONVERTER not found. Did you forget to build it?- Exit"
    exit 1
fi
if [ ! -d "$TARGETDIR" ]; then
    echo "creating build directory $TARGETDIR"
    mkdir "$TARGETDIR"
fi

FILESIZE=$(stat -c%s "$INPUTIMAGE")
# The ROUNDEDFILESIZE argument gives the usage of internal flash. Needs to be in 64k increments.
ROUNDEDFILESIZE=$(((FILESIZE + 65536) / 65536 * 65536 ))

# https://forum.odroid.com/viewtopic.php?t=31736 
# the image can be a 86x48 png which you convert to raw with ffmpeg:

ffmpeg -loglevel error -i "$TILEINPUTFILE" -f rawvideo -pix_fmt rgb565 "$TILEFILE"

# run mkfw to package everything:

$CONVERTER "$DESCR" "$TILEFILE" "$TARGETDIR/$1.fw"  0 16 $ROUNDEDFILESIZE app "$INPUTIMAGE"
echo $CONVERTER "$DESCR" "$TILEFILE" "$TARGETDIR/$1.fw" 0 16 $ROUNDEDFILESIZE app "$INPUTIMAGE"
echo "Done - $TARGETDIR/$1.bin generated. Copy it to the SD-Card and have fun :-)"