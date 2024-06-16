# CANSpy Dashboard

The CANSpy Dashboard is a small stand-alone- Webserver which provides the actual state to all connected browsers



## Standaloe Setup

For a standalone demo CANSpy can be installed on a raspberry pi (>= 3b) with the following steps:

Use the [Rasperry Pi Installer](https://www.raspberrypi.com/software/) to write the Raspberry OS onto a SD-card. Choose `Raspberry Pi OS Lite` as OS.

after installing the card, do in the boot root directory

    touch ssh
    nano userconfig

input just 

  pi:

add the encrypted password

  echo 'raspberry' | openssl passwd -6 -stdin >> userconfig
  nano userconfig

make sure that userconfig just contains username and encrypted password seperated by : in the first, single line of the userconfig file


boot the raspberry & connect via ssh

    ssh pi@raspberrypi

install docker 

    curl -fsSL https://get.Docker.com -o get-Docker.sh
    sudo sh get-Docker.sh
    sudo newgrp docker
    sudo usermod -aG docker $USER
    docker run hello-world


create hotspot

(TODO this chapter needs to be rewritten with the infos from https://raspberrytips.com/access-point-setup-raspberry-pi/, all setups shall be written in one single shell script for a setup for just the directory setup or also a whole raspberry setup )

create wpa passphrase    
    wpa_passphrase canspy canspycanspy

use the psk- output as password parameter for the next command (psk)

    sudo nmcli device wifi hotspot ssid canspy password <psk> ifname wlan0

the command returns a success message with a uuid for this connection


    Device 'wlan0' successfully activated with 'a12e6a66-b6ef-44fb-962a-5fa690ee0bed'

activate the hotspot permanenty after each boot

    sudo nmcli connection modify <uuid> connection.autoconnect yes connection.autoconnect-priority 100

set dhcp 

    sudo nmcli con modify Hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared

verify the correct settings

    sudo nmcli connection show a12e6a66-b6ef-44fb-962a-5fa690ee0bed

or with a text- gui

    sudo nmtui


clone Canspy

    git clone https://github.com/stko/canspy

go to the dashboard dir
    
    cd canspy/dashboard/

Mosquitto mqtt wants a predefined config to run

    sudo mkdir -p data/mqtt/config
    sudo nano data/mqtt/config/mosquitto.conf

with the content

    persistence true
    persistence_location /mosquitto/data
    log_dest file /mosquitto/log/mosquitto.log
    listener 1883

    ## Authentication ##
    #allow_anonymous false
    #password_file /mosquitto/config/password.txt


Noderea needs a data directory with write rights 


    mkdir -p  data/nodered
    sudo chmod a+rwx data/nodered


create some configs



    {
        "actual_settings": {
            "www_root_dir": "/app/static"
        },
        "server_config": {
            "credentials": "",
            "host": "0.0.0.0",
            "openbrowser": true,
            "port": 8000,
            "secure": false
        }
    }




the `docker compose build` command will build the container and run it interactive


## Reference
The dashboard is made out of the [WAS- Template](https://github.com/stko/was)