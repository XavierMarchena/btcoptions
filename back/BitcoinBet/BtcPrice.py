# -*- coding: UTF-8 -*
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import threading
from Cache._cache import Cache
import time


class Price:
	def __init__(self):
		self._cach = Cache()

	def main(self):
		while True:
			try:
				_bs_price = float(self._cach.GetCache('btc_bs'))  # float(client.get('btc_bs'))
				_bm_price = float(self._cach.GetCache('btc_bm'))  # float(client.get('btc_bm'))
				_total = _bs_price + _bm_price
				_avg = _total / 2
				_avg = float("{0:.2f}".format(_avg))
				self._cach.SetCache('btc_avg', _avg)
				time.sleep(1)
				print _avg
			except:
				print "btc_avg except"


_pc = Price()
_pc.main()