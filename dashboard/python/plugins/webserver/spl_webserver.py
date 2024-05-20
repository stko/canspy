#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json
from base64 import b64encode
import argparse
import time
import webbrowser

import socket

from jsonstorage import JsonStorage
from flask import Flask, render_template, send_from_directory, request
from werkzeug.datastructures import Headers
from flask_sockets import Sockets, Rule
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from pprint import pprint

from io import StringIO
from splthread import SplThread
import defaults


# Add the directory containing your module to the Python path (wants absolute paths)

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))

sys.path.append(os.path.abspath(ScriptPath))

# own local modules


class WebsocketUser:
	'''handles all user related data
	'''

	def __init__(self, name, ws):
		self.name = name
		self.ws = ws


class SplPlugin(SplThread):
	plugin_id = 'webserver'
	plugin_names = ['Flask Webserver']

	def __init__(self, modref):
		''' creates the HTTP and websocket server
		'''

		self.modref = modref
		self.program_dir = os.path.dirname(__file__)
		super().__init__(modref.message_handler, self)
		# reads the config, if any
		self.config = JsonStorage('webserver', 'backup', "config.json",
			{
				'server_config': {
					"credentials": "",
					"host": "0.0.0.0",
					"port": 8000,
					"secure": False,
					"openbrowser" : True
				},
				'actual_settings': {
					'www_root_dir': os.path.realpath(os.path.join(self.program_dir,'../../../static'))
				}

			})
		server_config = self.config.read("server_config", {})
		# set up the argument parser with values from the config
		parser = argparse.ArgumentParser()
		parser.add_argument("--host", default=server_config["host"],
							help="the IP interface to bound the server to")
		parser.add_argument("-p", "--port", default=server_config["port"],
							help="the server port")
		parser.add_argument("-s", "--secure", action="store_true", default=server_config["secure"],
							help="use secure https: and wss:")
		parser.add_argument("-c", "--credentials",  default=server_config["credentials"],
							help="user credentials")
		parser.add_argument("-b", "--browser", action="store_true", default=server_config["openbrowser"],
							help="opens a browser window")
		self.args = parser.parse_args()
		self.app = Flask('webserver')
		self.sockets = Sockets(self.app)
		self.ws_clients = []  # my actual browser connections
		self.modref.message_handler.add_event_handler(
			'webserver', 0, self.event_listener)
		# https://githubmemory.com/repo/heroku-python/flask-sockets/activity
		self.sockets.url_map.add(
			Rule('/ws', endpoint=self.on_create_ws_socket, websocket=True))


		'''
		@self.app.route('/')
		def index(path="index.html"):
			return send_from_directory(os.path.join(self.config.read('actual_settings')['www_root_dir'],""), path)
		'''

		@self.app.route('/', defaults={'path': 'index.html'})
		@self.app.route('/<path:path>')
		def catch_all(path):
			return send_from_directory(os.path.join(self.config.read('actual_settings')['www_root_dir'],""), path)


	def on_create_ws_socket(self, ws):
		''' distributes incoming messages to the registered event handlers

		Args:
			message (:obj:`str`): json string, representing object with 'type' as identifier and 'config' containing the data
		'''
		user=self.find_user_by_ws(ws)
		if user:
			if user != ws:
				self.disconnect()
				user=self.connect(ws)
		else:
			user=self.connect(ws)
		while not ws.closed:
			message = ws.receive()
			if message:
				#self.log_message('websocket received "%s"', str(message))
				try:
					data = json.loads(message)
					self.modref.message_handler.queue_event(
						user.name, defaults.MSG_SOCKET_MSG, data)
				except Exception as ex:
					print("message Exception:",str(ex))
					#self.log_message('%s', 'Invalid JSON')
					pass
				#self.log_message('json msg: %s', message)

	def connect(self, ws):
		''' thows a connect event about that new connection
		'''
		#self.log_message('%s', 'websocket connected')
		user = WebsocketUser(None, ws)
		self.ws_clients.append(user)
		self.modref.message_handler.queue_event(
			user.name, defaults.MSG_SOCKET_CONNECT, None)
		return user

	def find_user_by_ws(self, ws):
		for user in self.ws_clients:
			if user.ws == ws:
				return user
		return None

	def find_user_by_user_name(self, user_name):
		for user in self.ws_clients:
			if user.name == user_name:
				return user
		return None

	def disconnect(self):
		''' thows a close event about the closed connection
		'''
		user = self.find_user_by_user_name(None)
		if user:
			user.ws.close()
			self.ws_clients.remove(user)
		self.ws = None
		#self.log_message('%s', 'websocket closed')
		self.modref.message_handler.queue_event(
			self.user, defaults.MSG_SOCKET_CLOSE, None)

	def emit(self, type, config):
		''' sends data object as JSON string to websocket client

		Args:
		type (:obj:`str`): string identifier of the contained data type
		config (:obj:`obj`): data object to be sent
		'''

		message = {'type': type, 'config': config}
		user = self.find_user_by_user_name(None)
		pprint(message)
		if user.ws:
			if not user.ws.closed:
				user.ws.send(json.dumps(message))
			else:
				self.ws_clients.remove(user)

	def event_listener(self, queue_event):
		''' checks all incoming queue_events if to be send to one or all users
		'''
		#print("webserver event handler",queue_event.type,queue_event.user)
		if queue_event.type == defaults.MSG_SOCKET_MSG:
			message = {'type': queue_event.data['type'], 'config': queue_event.data['config']}
			json_message=json.dumps(message)
			dead_users=[]
			for user in self.ws_clients:
				if queue_event.user == None or queue_event.user == user.name:
					try:
						user.ws.send(json_message)
					except Exception as ex:
						print("Websocket send error",str(ex))
						dead_users.append(user)
			for user in dead_users:
				self.ws_clients.remove(user)

			return None  # no futher handling of this event
		return queue_event

	def _run(self):
		''' starts the server
		'''
		try:
			self.server = pywsgi.WSGIServer(
				(self.args.host, self.args.port), self.app, handler_class=WebSocketHandler)
			## read the epa dir with the actual settings

			if self.args.secure:
				print('initialized secure https server at port %d' %
					(self.args.port))
				webbrowser.open(f'https://{self.extract_ip()}:{self.args.port}', new=2)
			else:
				print('initialized http server at port %d' % (self.args.port))
			if self.args.browser:
				webbrowser.open(f'http://{self.extract_ip()}:{self.args.port}', new=2)

			self.server.serve_forever()

			#os.chdir(origin_dir)
		except KeyboardInterrupt:
			print('^C received, shutting down server')
			self.server.stop()

	def _stop(self):
		self.server.stop()

	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass

	# https://www.delftstack.com/de/howto/python/get-ip-address-python/
	def extract_ip(self):
		st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:       
			st.connect(('10.255.255.255', 1))
			IP = st.getsockname()[0]
		except Exception:
			IP = '127.0.0.1'
		finally:
			st.close()
		return IP


if __name__ == '__main__':
	class ModRef:
		store = None
		message_handler = None

	modref = ModRef()
	ws = SplPlugin(modref)
	ws.run()
	while True:
		time.sleep(1)
	ws.stop()
