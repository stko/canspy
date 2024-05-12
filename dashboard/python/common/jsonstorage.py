#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import canspy_dashboardlogger
from directorymapper import DirectoryMapper

logger = canspy_dashboardlogger.getLogger(__name__)

class JsonStorage:
	'''loads and saves persistent data as json to disk

	'''

	def __init__(self, module_name,storage_type,filename, default):
		'''
		creates a persistent data link to a config file on disk

		Args:
			module_name (:obj:`obj`) : instance the file belongs to
			storage_type (:str:`str`): identifier of the wanted storage type
			filename (:str:`str`):config file name without! path
			default (:obj:`obj`) : serialisable data structure to be used if file does not exist yet

		'''
		self.config = default # just the default
		self.file_name = filename
		self.module_name=module_name
		self.storage_type=storage_type

		try:
			with DirectoryMapper.open(self.module_name, self.storage_type,self.file_name) as json_file:
				self.config = json.load(json_file)

		except Exception as ex:
			logger.warning(
				"couldn't load config file {0}:{1}".format(self.file_name,str(ex)))
			# self default config to have a configable file on disk
			self.save()


	def read(self, key, default=None):
		''' read value from config, identified by key

			if key does not exist, the key and the default value is added to the config to make the key visible
			as a preparation for a potential later config editor
		Args:
		key (:obj:`str`): lookup index. if key == 'all', it returns the whole config object
		'''

		if key=='all':
			return self.config
		if key in self.config:
			return self.config[key]
		else:
			self.config[key]=default
			self.save()
		return default

	def write(self, key, value, delay_write=False):
		''' write value into config, identified by key.
		Saves also straight to disk, if delay_write is not True

		Args:
		key (:obj:`str`): lookup index
		value (:obj:`obj`): value to store
		delay_write (:obj:`boolean`): Do not save now
		'''

		self.config[key] = value
		if not delay_write:
			self.save()

	def save(self):
		''' write config to disk
		'''

		try:
			with DirectoryMapper.open(self.module_name, self.storage_type,self.file_name, 'w') as outfile:
				try:
					json.dump(self.config, outfile, sort_keys=True,
							indent=4, separators=(',', ': '))
					return
				except Exception as ex: 
					pass
			# json seems to throw an error when try to sort and numeric and string keys are mixed in a dict, so we try again without sort
			with DirectoryMapper.open(self.module_name, self.storage_type,self.file_name, 'w') as outfile:
				try:
					json.dump(self.config, outfile,
							indent=4, separators=(',', ': '))
				except Exception as ex2:
					logger.warning("couldn't write unsorted config file {0}: {1}".format(
						self.file_name,str(ex2)))
		except Exception as ex:
			logger.warning("couldn't write config file {0}: {1}".format(
				self.file_name,str(ex)))

