#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from messagehandler import Query
import defaults
from splthread import SplThread
from jsonstorage import JsonStorage
import sys
import os
import ssl
import json
from base64 import b64encode
import argparse
import time
import copy
from io import StringIO
import threading
import uuid
from pprint import pprint

# Non standard modules (install with pip)

#ScriptPath = os.path.realpath(os.path.join(
#	os.path.dirname(__file__), "./common"))


# Add the directory containing your module to the Python path (wants absolute paths)
#ys.path.append(os.path.abspath(ScriptPath))
# own local modules


class SplPlugin(SplThread):
	plugin_id = 'canspy_dashboard'
	plugin_names = ['Canspy Dashboard']

	def __init__(self, modref):
		''' inits the plugin
		'''
		self.modref = modref

		# do the plugin specific initialisation first

		# self.movielist_storage = JsonStorage(self.plugin_id, 'runtime', "canspy_dashboard.json", {'movielist': {}}) # set defaults

		self.lock = threading.Lock() # create a lock, only if necessary

		# at last announce the own plugin
		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)
		self.runFlag = True

	def event_listener(self, queue_event):
		''' try to send simulated answers
		'''
		#print("uihandler event handler", queue_event.type, queue_event.user)
		if queue_event.type == defaults.MSG_SOCKET_xxx:
			pass
		if queue_event.type == "_join":
			print("a web client has connected",queue_event.data)
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		# print("canspy_dashboard handler query handler", queue_event.type,  queue_event.user, max_result_count)
		if queue_event.type == defaults.MSG_SOCKET_xxx: # wait for defined messages
			pass
		return[]

	def _run(self):
		''' starts the server
		'''
		while self.runFlag:
			time.sleep(10)
			with self.lock:
				pass

	def _stop(self):
		self.runFlag = False

	# ------ plugin specific routines
