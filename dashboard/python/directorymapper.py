#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import canspy_dashboardlogger

logger = canspy_dashboardlogger.getLogger(__name__)


class DirectoryMapper:
	'''in some environments like docker it is essential to map directories to some other locations

	This DirectoryMapper creates class specific subdirectories in predefined parent folders,
	where then each class can store it's own files without taking care about the real location

	'''

	path_settings = {}

	@classmethod
	def __init__(cls, root_path, initial_path_settings):
		if cls.path_settings:
			logger.error(
				'multiple initialization: pathsettings already initialized!')
		cls.path_settings = initial_path_settings
		cls.root_path = root_path

	@classmethod
	def abspath(cls, module_name, storage_type, file_name, create_dirs=False):
		'''
		returns the absolut path of the requested storage_type,

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path

		'''
		if not cls.path_settings:
			logger.error('DirectoryMapper not initialized!')
			raise IOError
		if not storage_type in cls.path_settings:
			logger.error(f'unknown storage type {storage_type}')
			raise IOError
		owner_dir = os.path.abspath(os.path.join(
			cls.root_path, cls.path_settings[storage_type], module_name))
		if create_dirs and not os.path.exists(owner_dir):
			os.makedirs(owner_dir)
		full_file_name = os.path.join(owner_dir, file_name)
		return full_file_name

	@classmethod
	def open(cls, module_name, storage_type, file_name, rw_type='r',encoding="utf8"):
		'''
		identifies the absolut path of the requested storage_type,
		creates a owner class specific subfolder and returns the file handle

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path
						rw_type (:str:`str`) : file opening mode

		'''
		if not cls.path_settings:
			logger.error('DirectoryMapper not initialized!')
			raise IOError
		if not storage_type in cls.path_settings:
			logger.error(f'unknown storage type {storage_type}')
			raise IOError
		owner_dir = os.path.abspath(os.path.join(
			cls.root_path, cls.path_settings[storage_type], module_name))
		if not os.path.exists(owner_dir):
			os.makedirs(owner_dir)
		full_file_name = os.path.join(owner_dir, file_name)
		return open(full_file_name, rw_type,encoding=encoding)

	@classmethod
	def isdir(cls, module_name, storage_type, file_name):
		'''
		identifies if absolut path of the requested storage_type is a directory

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path

		'''
		full_file_name = cls.abspath(module_name, storage_type, file_name)
		return os.path.isdir(full_file_name)

	@classmethod
	def isfile(cls, module_name, storage_type, file_name):
		'''
		identifies if absolut path of the requested storage_type is a file

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path

		'''
		full_file_name = cls.abspath(module_name, storage_type, file_name)
		return os.path.isfile(full_file_name)

	@classmethod
	def access(cls, module_name, storage_type, file_name, access_mode):
		'''
		identifies if absolut path of the requested storage_type is accecible

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path
						access_mode (:obj:`obj`):access mode

		'''
		full_file_name = cls.abspath(module_name, storage_type, file_name)
		return os.access(full_file_name, access_mode)

	@classmethod
	def getmtime(cls, module_name, storage_type, file_name):
		'''
		gets the file time

		Args:
						module_name (:str:`str`) : who the file belongs to
						storage_type (:str:`str`): identifier of the wanted storage type
						file_name (:str:`str`):file name without! path

		'''
		full_file_name = cls.abspath(module_name, storage_type, file_name)
		return os.path.getmtime(full_file_name)
