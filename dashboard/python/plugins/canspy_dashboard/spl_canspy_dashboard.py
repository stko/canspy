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
from byteformatter import format_msgs
from evalidate import Expr, EvalException
from bitstring import BitArray  # nice module for bit wise operations

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
                "msg_max_age": 300,
            },
        )  # set defaults

        self.module_defaults = JsonStorage(
            self.plugin_id,
            "backup",
            "module_defaults.json",
            {
                "sensors": {
                    "batt": {
                        "3 if not value_raw < 21.0 else 0": "Battery is empty: {value_raw}V",
                        "2 if not value_raw < 23.0 else 0": "Battery Voltage {value_raw} is too low",
                        "1": "{value_raw} V is ok",
                    }
                },
                "vehiclelines": {
                    "Defender": {
                        "modules": {
                            "A63": {
                                "msgs": [
                                    {
                                        "id": "0x181",
                                        "mask": "0xFFF",
                                        "assessments": [
                                            {
                                                "getvalue": "b:7:1:0:0:0:Aus&An",
                                                "evaluations": {
                                                    "3 if not value_raw else 0": "{value} is too high",
                                                    "1": "{value} is nice",
                                                },
                                            }
                                        ],
                                    },
                                    {"id": "0x182", "mask": "0xFFF"},
                                ]
                            },
                            "A70": {"msgs": {"0x425": "0xFFF"}},
                            "A99": {"msgs": {"0x406": "0xFFF"}},
                            "Aerror": {"msgs": {"0x425": "0x000"}},
                            "Axx": {"msgs": {"0x999": "0xFFF"}},
                        }
                    }
                },
            },
        )  # set defaults
        # collecting all device results
        self.dashboard_summary = {}
        self.device_data = {}
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
                with self.lock:
                    self.modref.message_handler.queue_event(
                        None,
                        defaults.MSG_SOCKET_MSG,
                        {
                            "type": defaults.BROADCAST_canspy_dashboard_LIST,
                            "config": self.generate_broadcast(),
                        },
                    )
                    self.last_broadcast_time = time.time()

            self.mqtt_client.loop()

    def _stop(self):
        self.runFlag = False

    # ------ plugin specific routines

    def on_mqtt_message(self, client, userdata, message):
        device_msg = str(message.payload.decode("utf-8"))
        print("data received: ", datetime.now(), device_msg)
        print("message topic: ", message.topic)
        topic_elements = message.topic.split("/")
        if len(topic_elements) == 4 and topic_elements[3] == "data":
            device_id = topic_elements[2]
            print("can data:", device_id, device_msg)
            client_answer = None
            try:
                client_answer = self.update_datapool(device_id, json.loads(device_msg))
            except json.JSONDecodeError as ex:
                print("JSON Data format error:", str(ex))
            if client_answer:
                topic = "/canspy/%/config".replace("%", device_id)
                print(topic)
                client.publish(
                    topic,
                    json.dumps(client_answer),
                    qos=self.settings.read("mqtt_qos"),
                )

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT Broker: " + self.settings.read("mqtt_host"))
        client.subscribe(self.settings.read("mqtt_topic"))

    def update_datapool(self, device_id: str, device_msg: dict) -> dict:
        """
        updates all relevant data sets

        update_datapool takes the incoming dataset from a iot device.

        if the dataset contains a refresh flag as an indication of a rebooted device, it
        just send the last stored one (if any) to refresh the iot display

        It calculates the new display content based on the received values, identifies if
        the display content has changed and so needs to be updated, it also updates
        the broadcast values

        """
        if not device_msg:
            return {}
        device_data_has_changed = False
        # get the root data to read the available vehicles out of it
        root_config_data = self.module_defaults.read("all")
        # do we have already the device_data for that device?
        if device_id not in self.device_data:
            self.device_data[device_id] = {
                "location": root_config_data["locations"][0],
                "vehicle_line": list(root_config_data["vehiclelines"].keys())[0],
                "friendly_name": device_id,
                "config": {},
            }
        vehicle_line = self.device_data[device_id]["vehicle_line"]
        self.device_data[device_id]["lastmsg_time"] = time.time()
        self.device_data[device_id]["last_msg"] = device_msg
        new_device_config = {}  # (re-)build the config for the device

        for module, module_data in root_config_data["vehiclelines"][vehicle_line][
            "modules"
        ].items():
            new_device_config_msgs = []  # create new msgs dict
            new_device_config_info = []  # create new msgs dict
            new_device_config[module] = {
                "msgs": new_device_config_msgs,
                "info": new_device_config_info,
            }
            for msg in module_data["msgs"]:
                new_device_config_msgs.append({"id": msg["id"], "mask": msg["mask"]})
                for can_id, can_msg in device_msg["can"].items():
                    if int(can_id) & int(msg["mask"], 16) == int(
                        msg["id"], 16
                    ):  # can-id matches to mask
                        if "assessments" not in msg:
                            continue
                        for assessment in msg[
                            "assessments"
                        ]:  # go through all assessments
                            value, value_raw = format_msgs(
                                bytes.fromhex(can_msg["msg"]), assessment["getvalue"]
                            )
                            for evaluation, output_format in assessment[
                                "evaluations"
                            ].items():
                                eval_state = Expr(evaluation).eval(
                                    {"value": value, "value_raw": value_raw}
                                )
                                if eval_state:
                                    info_text = output_format.format(
                                        **{"value": value, "value_raw": value_raw}
                                    )
                                    print(eval_state, info_text)
                                    new_device_config_info.append(
                                        {"state": eval_state, "text": info_text}
                                    )
                                    self.set_dashboard_summary_value(
                                        self.device_data[device_id]["location"],
                                        device_id,
                                        self.device_data[device_id]["friendly_name"],
                                        module,
                                        "msg."
                                        + ".".join(
                                            [
                                                msg["id"],
                                                msg["mask"],
                                                assessment["getvalue"],
                                            ]
                                        ),
                                        eval_state,
                                        info_text,
                                    )
                                    break
        for sensor, sensor_evaluations in root_config_data["sensors"].items():
            if sensor not in device_msg["sensors"]:
                continue
            new_device_config_info = []  # create new msgs dict
            new_device_config["sensors"] = {
                "info": new_device_config_info,
            }
            value_raw = device_msg["sensors"][sensor]
            for evaluation, output_format in sensor_evaluations.items():
                eval_state = Expr(evaluation).eval({"value_raw": value_raw})
                if eval_state:
                    info_text = output_format.format(**{"value_raw": value_raw})
                    print(eval_state, info_text)
                    new_device_config_info.append(
                        {"state": eval_state, "text": info_text}
                    )
                    self.set_dashboard_summary_value(
                        self.device_data[device_id]["location"],
                        device_id,
                        self.device_data[device_id]["friendly_name"],
                        "sensors",
                        "sensor." + sensor,
                        eval_state,
                        info_text,
                    )
                    break

        # return self.module_defaults.read("vehiclelines")[vehicle_line]["modules"]
        for module_data in new_device_config.values():
            module_state = (
                0  # calculate module state based on it's dfferent info states
            )
            for info in module_data["info"]:
                if info["state"] > module_state:
                    module_state = info["state"]
            module_data["state"] = module_state
        if False and self.dicts_equal(
            new_device_config, self.device_data[device_id]["config"]
        ):
            return None
        else:
            self.device_data[device_id][
                "config"
            ] = new_device_config  # (re-)build the config for the device
            return new_device_config

    def dicts_equal(self, dict1, dict2):
        """
        originalgetreu geschrieben von ChatGPT4.0o
        Überprüft, ob zwei verschachtelte Dictionaries gleich sind.

        :param dict1: Erstes Dictionary
        :param dict2: Zweites Dictionary
        :return: True, wenn die Dictionaries gleich sind, sonst False
        """
        if dict1 is dict2:
            return True

        if dict1.keys() != dict2.keys():
            return False

        for key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                if not self.dicts_equal(dict1[key], dict2[key]):
                    return False
            else:
                if dict1[key] != dict2[key]:
                    return False

        return True

    def set_dashboard_summary_value(
        self,
        location: str,
        device_id: str,
        friendly_name: str,
        module: str,
        unique_id: str,
        state: int,
        info_text: str,
    ):
        if location not in self.dashboard_summary:
            self.dashboard_summary[location] = {"devices": {}}
        location_dict = self.dashboard_summary[location]
        if device_id not in location_dict["devices"]:
            location_dict["devices"][device_id] = {"friendly_name": "", "modules": {}}
        device_dict = location_dict["devices"][device_id]
        device_dict["friendly_name"] = friendly_name
        if module not in device_dict["modules"]:
            device_dict["modules"][module] = {"infos": {}}
        module_dict = device_dict["modules"][module]
        module_dict["infos"][unique_id] = {
            "timestamp": time.time(),  # stores the update time as secs float
            "state": state,
            "info_text": info_text,
        }

    def generate_broadcast(self):
        """
        Transforms the collected dashboard_summary data into the broadcast_data which send to the web dashboard
        """
        # the color lockup-table
        color_lookup = ["grey", "green", "orange", "red"]
        # at first delete old dead data
        actual_time = time.time()
        msg_max_age = self.settings.read("msg_max_age", 300)
        location_to_delete = []
        for location, location_data in self.dashboard_summary.items():
            if "state" not in location_data:
                location_data["state"] = 0
            device_to_delete = []
            for device_id, device_data in location_data["devices"].items():
                if "state" not in device_data:
                    device_data["state"] = 0
                module_to_delete = []
                for module, module_data in device_data["modules"].items():
                    if "state" not in module_data:
                        module_data["state"] = 0
                    info_to_delete = []
                    for info_id, info in module_data["infos"].items():
                        if info["timestamp"] < actual_time - msg_max_age:
                            info_to_delete.append(info_id)
                    for info_id in info_to_delete:
                        del module_data["infos"][info_id]
                    if not module_data["infos"]:  # no infos left
                        module_to_delete.append(module)
                for module_id in module_to_delete:
                    del device_data["modules"][module_id]
                if not device_data["modules"]:  # no modules left
                    device_to_delete.append(device_id)
            for device_id in device_to_delete:
                del location_data["devices"][device_id]
            if not location_data["devices"]:  # no modules left
                location_to_delete.append(location)

        # spread the states from the single items bottom- up to the locations
        for location, location_data in self.dashboard_summary.items():
            for device_id, device_data in location_data["devices"].items():
                for module, module_data in device_data["modules"].items():
                    for info_id, info in module_data["infos"].items():
                        if module_data["state"] < info["state"]:
                            module_data["state"] = info["state"]
                        if device_data["state"] < info["state"]:
                            device_data["state"] = info["state"]
                        if location_data["state"] < info["state"]:
                            location_data["state"] = info["state"]

        # create the Vue treeview data
        broadcast_data = []
        for location, location_data in self.dashboard_summary.items():
            device_children = []
            for device_id, device_data in location_data["devices"].items():
                module_children = []
                for module, module_data in device_data["modules"].items():
                    info_children = []
                    for info_id, info in module_data["infos"].items():
                        info_children.append(
                            {
                                "title": info["info_text"],
                                "color": color_lookup[info["state"]],
                                "icon": "gauge",
                                # "children": module_children,
                            }
                        )
                    module_children.append(
                        {
                            "title": module,
                            "color": color_lookup[module_data["state"]],
                            "icon": "module",
                            "children": info_children,
                        }
                    )
                device_children.append(
                    {
                        "title": device_data["friendly_name"] + " (" + device_id + ")",
                        "color": color_lookup[device_data["state"]],
                        "icon": "vehicle",
                        "children": module_children,
                    }
                )
            broadcast_data.append(
                {
                    "title": location,
                    "color": color_lookup[location_data["state"]],
                    "icon": "location",
                    "children": device_children,
                }
            )
        return broadcast_data
        """
        [
            {
                "title": "Bremerhaven",
                "color": "green",
                "icon": "location",
                "children": [
                    {
                        "title": "6700622",
                        "icon": "vehicle",
                        "color": "orange",
                        "children": [
                            {
                                "title": "A32",
                                "icon": "module",
                                "color": "orange",
                                "children": [
                                    {
                                        "title": "logo.png",
                                        "icon": "gauge",
                                        "color": "red",
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
        ]
"""
