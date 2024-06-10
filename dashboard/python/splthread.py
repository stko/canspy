#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import threading
from abc import ABCMeta, abstractmethod
import defaults

class SplThread(metaclass=ABCMeta):
	'''Partly abstract class to implement threading & message handling
	'''

	def __init__(self, msg_handler, child):
		self.msg_handler = msg_handler
		self.child = child

	@abstractmethod
	def _run(self):
		''' starts the thread loop
		'''
		pass

	@abstractmethod
	def _stop(self):
		''' stops the thread loop
		'''
		pass

	@abstractmethod
	def  event_listener(self, queue_event):
		''' handler for system events
		'''
		pass

	@abstractmethod
	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass

	def run(self):
		''' starts the child thread
		'''
		# Create a Thread with a function without any arguments
		#th = threading.Thread(target=_ws_main, args=(server,))
		self.th = threading.Thread(target=self.child._run)
		# Start the thread
		self.th.setDaemon(True)
		self.th.start()

	def stop(self, timeout=0):
		''' stops the child thread. If timeout > 0, it will wait timeout secs for the thread to finish
		'''
		self.child._stop()
		if timeout > 0:
			self.th.join(timeout)
		return self.th.isAlive()

	def user_message(self,user,user_message, user_button_text='OK'):
		self.msg_handler.queue_event(user, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_APP_USER_MESSAGE, 'config': {'user_message': user_message,'user_button_text':user_button_text}})
