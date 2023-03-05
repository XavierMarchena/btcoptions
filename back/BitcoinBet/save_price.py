# -*- coding: UTF-8 -*
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import datetime
import sys
import threading
from btc_model import BtcRange
from Cache._cache import Cache
import threading
import time

class SavePrice:
	def __init__(self):
		self._cache = Cache()

	def save(self):
		while True:
			try:
				btc_range = BtcRange(price=self._cache.GetCache('btc_avg'))
				btc_range.save()
				time.sleep(60)
				print "Price Saved"
			except Exception as e:
				print(e)

	def run(self):
		_my = threading.Thread(target=self.save, args=())
		_my.daemon = True
		_my.start()
		_my.join()
		while True:
			if not _my.isAlive():
				_my = threading.Thread(target=self.save, args=())
				_my.daemon = True
				_my.start()
				_my.join()

_pc = SavePrice()
_pc.run()
