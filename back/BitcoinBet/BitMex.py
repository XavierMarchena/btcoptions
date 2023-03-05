# -*- coding: UTF-8 -*
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Cache._cache import Cache
import websocket
import json
import time
import threading
import ssl


class BitMex:
	def __init__(self):
		self.url = "wss://www.bitmex.com/realtime?subscribe=trade:XBTUSD"
		self.price = 0
		self._cach = Cache()

	def get_price(self):
		#client = Client(('localhost', 11211))
		ws = websocket.create_connection(self.url, sslopt={"cert_reqs": ssl.CERT_NONE})
		while True:
			result =  ws.recv()
			_json = json.loads(result)
			try:
				self.price = _json['data'][0]['price']
			except:
				self.price = 0

			if self.price != 0:
				#client.set('btc_bm', float(self.price))
				self._cach.SetCache('btc_bm', float(self.price))
			#time.sleep(0.5)
			print self.price


def main():
	_bm = BitMex()
	_my = threading.Thread(target=_bm.get_price, args=())
	_my.daemon = True
	_my.start()
	_my.join()
	log = open("gs_log.log", "a")
	while True:
		if not _my.isAlive():
			log.write("error!\r\n")
			_my = threading.Thread(target=_bm.get_price, args=())
			_my.daemon = True
			_my.start()
			_my.join()


if __name__ == "__main__":
	main()

