# -*- coding: UTF-8 -*
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pymemcache.client.base import Client
from Settings.settings import Settings

class Cache:
	def __init__(self):
		_sett = Settings()
		_raw_cache = _sett.get_cache
		self.client = Client((_raw_cache['ip'], _raw_cache['port']))

	def SetCache(self, key, value):
		self.client.set(key, value)

	def GetCache(self, key):
		return self.client.get(key)