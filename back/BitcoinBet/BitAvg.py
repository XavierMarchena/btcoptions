
import hashlib
import hmac
import requests
import time
import threading
from pymemcache.client.base import Client
import json
import websocket

class BitAvg:
	def __init__(self):
		self.secret_key = "ZmM4M2EwMWI1YzdkNDU2MmExZDQ3ZWI4N2Y3MzNjNDRlYjhmYTUzMjJjMTQ0MWVhYjIyZGJmODdkNzdkYzllYw"
		self.public_key = "YWExZTgyNDc5ZDZhNGI1ZWFiZmYyYmQ5ZTBmMTFkM2I"
		self.ticket_url = "https://apiv2.bitcoinaverage.com/websocket/get_ticket"
		self.price = 0

	def get_price(self):
		client = Client(('localhost', 11211))
		timestamp = int(time.time())
		payload = '{}.{}'.format(timestamp, self.public_key)
		hex_hash = hmac.new(self.secret_key.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
		signature = '{}.{}'.format(payload, hex_hash)
		ticket_url = "https://apiv2.bitcoinaverage.com/websocket/get_ticket"
		ticket_header = {"X-signature": signature}
		ticket = requests.get(url=ticket_url, headers=ticket_header)#.json()
		url = "wss://apiv2.bitcoinaverage.com/websocket/ticker?public_key={}&ticket={}".format(self.public_key, ticket)
		ws = websocket.create_connection(url)
		subscribe_message = json.dumps({"event": "message", "data": {"operation": "subscribe","options": {"currency": "BTCUSD","market": "local"}}})
		ws.send(subscribe_message)
		while True:
			result =  ws.recv()
			_json = json.loads(result)
			try:
				self.price = _json['data']['last']
			except:
				self.price = 0





_bta = BitAvg()
_bta.get_price()
