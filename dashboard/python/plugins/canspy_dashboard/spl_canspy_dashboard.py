#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from messagehandler import Query
import defaults
from splthread import SplThread
from jsonstorage import JsonStorage
import json
from base64 import b64encode
import time
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from pprint import pprint


# Non standard modules (install with pip)

# ScriptPath = os.path.realpath(os.path.join(
# 	os.path.dirname(__file__), "./common"))


# Add the directory containing your module to the Python path (wants absolute paths)
# ys.path.append(os.path.abspath(ScriptPath))
# own local modules


class SplPlugin(SplThread):
    plugin_id = "canspy_dashboard"
    plugin_names = ["Canspy Dashboard"]

    def __init__(self, modref):
        """inits the plugin"""
        self.modref = modref

        # do the plugin specific initialisation first

        self.settings = JsonStorage(
            self.plugin_id,
            "backup",
            "canspy_dashboard.json",
            {
                "mqtt_topic": "/canspy/#",
                "mqtt_host": "schnipsl",
                "mqtt_port": 1883,
                "mqtt_qos": 1,
                "broadcast_interval": 5,
            },
        )  # set defaults

        self.module_defaults = JsonStorage(
            self.plugin_id,
            "backup",
            "module_defaults.json",
            {
                "modules": {
                    "A63": {"0x032": "0xFFF", "0x736": "0xFFF"},
                    "A70": {"0x425": "0xFFF"},
                    "A99": {"0x406": "0xFFF"},
                    "Aerror": {"0x425": "0x000"},
                    "Axx": {"0x999": "0xFFF"},
                }
            },
        )  # set defaults
        self.broadcast_data = [
            {
                "title": "Bremerhaven",
                "color": "green",
                "icon" : "location",
                "children": [
                    {
                        "title": "6700622",
                        "icon" : "vehicle",
                        "color" : "orange",
                        "children": [
                            {
                                "title": "logo.png",
                                "icon": "gauge",
                                "color" : "red"
                            },
                        ],
                    },
                ],
            },
        ]
        self.last_broadcast_time = time.time()

        self.lock = threading.Lock()  # create a lock, only if necessary

        # module specific setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(
            self.settings.read("mqtt_host"), self.settings.read("mqtt_port")
        )
        # at last announce the own plugin
        super().__init__(modref.message_handler, self)
        modref.message_handler.add_event_handler(self.plugin_id, 0, self.event_listener)
        modref.message_handler.add_query_handler(self.plugin_id, 0, self.query_handler)
        self.runFlag = True

    def event_listener(self, queue_event):
        """try to send simulated answers"""
        # print("uihandler event handler", queue_event.type, queue_event.user)
        if queue_event.type == defaults.MSG_SOCKET_xxx:
            pass
        if queue_event.type == "_join":
            print("a web client has connected", queue_event.data)
        # for further pocessing, do not forget to return the queue event
        return queue_event

    def query_handler(self, queue_event, max_result_count):
        # print("canspy_dashboard handler query handler", queue_event.type,  queue_event.user, max_result_count)
        if queue_event.type == defaults.MSG_SOCKET_xxx:  # wait for defined messages
            pass
        return []

    def _run(self):
        """starts the server"""
        while self.runFlag:
            # time.sleep(10)
            if (
                time.time() - self.settings.read("broadcast_interval", 5)
                > self.last_broadcast_time
            ):
                self.modref.message_handler.queue_event(
                    None,
                    defaults.MSG_SOCKET_MSG,
                    {
                        "type": defaults.BROADCAST_canspy_dashboard_LIST,
                        "config": self.broadcast_data,
                    },
                )
                self.last_broadcast_time=time.time()

            with self.lock:
                pass
            self.mqtt_client.loop()

    def _stop(self):
        self.runFlag = False

    # ------ plugin specific routines

    def on_mqtt_message(self, client, userdata, message):
        data = str(message.payload.decode("utf-8"))
        print("data received: ", datetime.now(), data)
        print("message topic: ", message.topic)
        topic_elements = message.topic.split("/")
        if len(topic_elements) == 4 and topic_elements[3] == "data":
            device_id = topic_elements[2]
            print("can data:", device_id, data)
            topic = "/canspy/%/config".replace("%", device_id)
            print(topic)
            client.publish(
                topic,
                json.dumps(self.module_defaults.read("all")),
                qos=self.settings.read("mqtt_qos"),
            )

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT Broker: " + self.settings.read("mqtt_host"))
        client.subscribe(self.settings.read("mqtt_topic"))
