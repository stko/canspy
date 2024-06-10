#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
import sys
import os
import importlib
import importlib.util
import traceback
import re

# Non standard modules (install with pip)


ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "./common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules
from jsonstorage import JsonStorage

class PluginManager():
	''' loads all canspy_dashboard plugins
	'''

	def __init__(self, modref, plugin_root_dir):
		self.origin_dir = os.path.dirname(__file__)
		self.config = JsonStorage('PluginManager', 'backup', "plugins.json", {
				'plugins':{

				}
			}
		)

		self.plugins = {}
		regex = re.compile(r'^spl_.+.py$')
		try:
			plugin_path = os.path.realpath(os.path.join(
				os.path.dirname(__file__), plugin_root_dir))
			list_subfolders_with_paths = [
				f.path for f in os.scandir(plugin_path) if f.is_dir()]
			new_plugins_found=False
			config_plugins=self.config.read('plugins')
			for sub_folder in list_subfolders_with_paths:
				list_file_infos = [f for f in os.scandir(
					sub_folder) if f.is_file()]
				for file_info in list_file_infos:
					if regex.match(file_info.name):
						print(file_info.path)

						module_spec = importlib.util.spec_from_file_location(file_info.name, file_info.path)
						my_module = importlib.util.module_from_spec(module_spec)
						module_spec.loader.exec_module(my_module)
						plugin_id=my_module.SplPlugin.plugin_id
						if not plugin_id in config_plugins: #new module
							config_plugins[plugin_id]={'active':False}
							new_plugins_found=True
							continue
						if not config_plugins[plugin_id]['active']:
							continue

						instance = my_module.SplPlugin(modref)
						self.plugins[file_info.name] =instance
			if new_plugins_found:
				self.config.write('plugins',config_plugins)
			#finally run all active modules
			for instance in self.plugins.values():
				instance.run()
		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)
