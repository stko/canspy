#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class Scheduler:
	''' helper object to handle a collection of functions which shall be called in a regular time interval

	When a negative time interval is given, then the function is called immediadly and it's waited for the next
	interval,
	With a positive interval it's waited first before the function is called
	'''

	def __init__(self, calls):
		''' calls is a list of functions and their wanted time interval
		'''
		self.task_list = {}
		for function, interval in calls:
			self.set(function, interval)

	def set(self, function, interval):
		act_time = time.time()
		if interval and function != None:
			if interval < 0:
				self.task_list[function] = {
					'interval': abs(interval), 'nexttick': 0}
			else:
				self.task_list[function] = {
					'interval': interval, 'nexttick': act_time+interval}

	def execute(self):
		for function, interval_data in self.task_list.items():
			act_time = time.time()
			if interval_data['nexttick'] <= act_time:
				function()
				interval_data['nexttick'] = act_time+interval_data['interval']


def myprint_1():
	print('1')


def myprint_2():
	print('2')


if __name__ == "__main__":
	a = Scheduler([(myprint_1, 2), (myprint_2, 4)])
	while True:
		a.execute()
		time.sleep(1)
