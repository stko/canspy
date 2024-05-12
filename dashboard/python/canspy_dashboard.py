#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
from directorymapper import DirectoryMapper
from messagehandler import MessageHandler
import canspy_dashboardlogger
from pluginmanager import PluginManager

class ModRef:
	''' helper class to store references to the global modules
	'''
	
	def __init__(self):
		self.server = None
		self.message_handler = None


def _(s): return s

logger = canspy_dashboardlogger.getLogger(__name__)

DirectoryMapper(os.path.abspath(os.path.dirname(__file__)),
	{
		'backup' : 'volumes/backup',
		'runtime' : 'volumes/runtime',
		'tmpfs' : 'volumes/tmpfs'
	}
)
modref = ModRef() # create object to store all module instances
modref.message_handler = MessageHandler(modref)
plugin_manager=PluginManager(modref,'plugins')

while(True):
	time.sleep(1)
