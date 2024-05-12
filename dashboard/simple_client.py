# !/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

import paho.mqtt.client as mqtt
import json

SUB_TOPIC = "/canspy/#"
BROKER_ADDRESS = "schnipsl"
PORT = 1883
QOS=1

def on_message(client, userdata, message):
	data = str(message.payload.decode("utf-8"))
	print("data received: ",datetime.now(), data)
	print("message topic: ", message.topic)
	topic_elements=message.topic.split("/")
	if len(topic_elements)==4 and topic_elements[3]=="data":
		device_id=topic_elements[2]
		print("can data:", device_id,data)
		DATA = '''
{
    "modules": {
        "A63": {
            "0x032": "0xFFF",
            "0x736": "0xFFF"
        },
        "A70": {
            "0x425": "0xFFF"
        },
        "A99": {
            "0x406": "0xFFF"
        },
        "Aerror": {
            "0x425": "0x000"
        },
        "Axx": {
            "0x999": "0xFFF"
        }
    }
}
'''
		## check data syntax and compress
		data=json.dumps(json.loads(DATA))
		topic = "/canspy/%/config".replace("%",device_id)
		print(topic)
		client.publish(topic, data, qos=QOS)

def on_connect(client, userdata, flags, rc):
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	client.subscribe(SUB_TOPIC)

if __name__ == "__main__":
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect(BROKER_ADDRESS, PORT)

	client.loop_forever()


