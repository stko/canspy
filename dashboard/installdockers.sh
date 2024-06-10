#!/bin/sh
export SUDO=$(which sudo)
$SUDO apt-get update
$SUDO find -name installdocker.sh -exec chmod a+rx {} \; -exec bash -c {}  \;

