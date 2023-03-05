import json
import os,sys,inspect
import random
import time
import uuid
from jsonschema import validate


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from mysql_helper import MysqlPython

import hashlib
from operator import itemgetter
from Core.bet_model import Tokens, Platforms, Players
from Settings.settings import Settings
import requests

import logging
import requests
from celery import Celery
import logging
import re

from celery.task import task

_sett = Settings()
_raw_mongo = _sett.get_mongo
_raw_redis = _sett.get_redis

BROKER_URL = _raw_redis['broker_url']

BACKEND_URL = _raw_redis['backend_url']

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL, include=["Core.bet_controller"])
# app.add_defaults({
#     'CELERYD_HIJACK_ROOT_LOGGER': False,
# })



#TODO: check make hash algorithm https://gitlab.com/xaviermarchena/btcoptions_leviathan/-/issues/27
def make_hash(_params,_casino_api_key):
	concatstr = ""
	for key, value in sorted(_params.items()):
		concatstr +=str(value)
		logging.info(concatstr)
		logging.info(key)
		logging.info(value)
		logging.info(type(value))

	sign = hashlib.md5()
	sign.update((concatstr + _casino_api_key).encode('utf-8'))
	logging.info(sign.hexdigest())
	return sign.hexdigest()


# etc

	# _new_json = ""
	#
	# _final = len(_params)
	# count = 0
	#
	# for k, v in sorted(_params.items(), key=itemgetter(0)):
	# 	count += 1
	# 	if count == _final:
	# 		#_new_json += "%s=%s" % (k, v)
	# 		_new_json += "%s" % (v)
	# 		logging.info(k)
	# 		logging.info(type(k))
	# 		logging.info(v)
	# 	else:
	# 		#_new_json += "%s=%s&" % (k, v)
	# 		_new_json += "%s" % (v)
	# 		logging.info(k)
	# 		logging.info(type(k))
	# 		logging.info(v)
	#
	# logging.info(_new_json)
	#
	# sign = hashlib.md5()
	# sign.update((_new_json + _casino_api_key).encode('utf-8'))
	# logging.info(sign.hexdigest())
	# return sign.hexdigest()

#READ JSON SCHEMAS FROM FILE

with open('/bitcoinbet/back/Api/authenticate_schema.json') as schemaf:
    authenticate_schema = json.loads('\n'.join(schemaf.readlines()))

with open('/bitcoinbet/back/Api/balance_request_schema.json') as schemaf:
    balance_request_schema = json.loads('\n'.join(schemaf.readlines()))

with open('/bitcoinbet/back/Api/balance_response_schema.json') as schemaf:
    balance_response_schema = json.loads('\n'.join(schemaf.readlines()))

with open('/bitcoinbet/back/Api/bet_request_schema.json') as schemaf:
    bet_request_schema = json.loads('\n'.join(schemaf.readlines()))

with open('/bitcoinbet/back/Api/bet_response_schema.json') as schemaf:
    bet_response_schema = json.loads('\n'.join(schemaf.readlines()))

with open('/bitcoinbet/back/Api/notificate_schema.json') as schemaf:
    notificate_schema = json.loads('\n'.join(schemaf.readlines()))

@app.task(bind=True, max_retries=3, name='Api.main.balance')
def balance(self, request_params_front):
	try:

		_platform_doc = Platforms.objects.filter(idgame=request_params_front["idgame"])#TODO GET WITH platform_id
		_casino_api_developer_id = _platform_doc[0].developer_id
		_casino_api_getbalance_url = _platform_doc[0].getbalance_url

		request_params_api = {'token': request_params_front["token"],
							  'DeveloperId': _casino_api_developer_id,
							  "timestamp": int(time.time())}

		#_platform_doc = Platforms.objects.filter(developer_id=_casino_api_developer_id)# TODO replace _casino_api_developer_id with idgame
		_casino_api_key = _platform_doc[0].key

		_hash = make_hash(request_params_api, _casino_api_key)
		request_params_api['Hash'] = _hash

		try:
			validate(instance=request_params_api, schema=balance_request_schema)
		except Exception, e:
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

		casino_api_response = requests.post(_casino_api_getbalance_url, json=request_params_api)

		try:
			validate(instance=casino_api_response.json(), schema=balance_response_schema)
		except Exception, e:
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


		return casino_api_response.json()
	except Exception, err:
		self.retry(exc=err, countdown=2 ** self.request.retries)

@app.task(bind=True, max_retries=3, name='Api.main.bet')
def bet(self, request_params_front):
	try:
		def formatNumber(num):
			if num % 1 == 0:
				return int(num)
			else:
				return num
			# else:
			# 	if request_params_front["currency"]=="USD":
			# 		return round(num, 3)
			# 	elif request_params_front["currency"]=="MBTC":
			# 		return num

		#Prepare json
		#_token_doc = Tokens.objects.filter(token=request_params_front["token"])
		#_casino_player_id = _token_doc[0].casino_player_id

		regex = re.compile('.*(%s).*' % request_params_front["token"])#TODO ADD CURRENCY FILTER
		#_bet_uuid = uuid.uuid1().hex
		# _token = Tokens.objects.filter(token=token)
		_player_doc = Players.objects(tokens=regex)#TODO ADD CURRENCY FILTER

		_platform_doc = Platforms.objects.filter(platform_id=_player_doc[0].platform_id)
		_casino_api_developer_id = _platform_doc[0].developer_id
		_casino_api_setbet_url = _platform_doc[0].setbet_url

		request_params_api = {'DeveloperId': str(_casino_api_developer_id),#todo
							  'token': str(request_params_front["token"]),
							  'UserId': str(_player_doc[0].casino_player_id),
							  'action': 'credit' if request_params_front["result"]["result"] == 'win' else 'debit',
							  'amount': formatNumber(float(request_params_front["amount_bet"])) if request_params_front["result"]["result"] == 'lose' else formatNumber(float(request_params_front["amount"])) if request_params_front["amount"] !=0 else int(request_params_front["amount"]) ,
							  'amount_bet': formatNumber(float(request_params_front["amount_bet"])) if request_params_front["amount_bet"]!=0 else int(request_params_front["amount_bet"]),
							  'amount_win': formatNumber(float(request_params_front["amount_win"])) if request_params_front["amount_win"]!= 0 else int(request_params_front["amount_win"]),
							  'round_id': int(request_params_front["round_id"]),#TODO,
							  'details': str(request_params_front["result"]["result"]),
							  'timestamp': int(time.time())}

		_platform_doc = Platforms.objects.filter(developer_id=_casino_api_developer_id)
		_casino_api_key = _platform_doc[0].key

		_hash = make_hash(request_params_api, _casino_api_key)
		request_params_api['Hash'] = _hash

		try:
			validate(instance=request_params_api, schema=bet_request_schema)
		except Exception, e:
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

		casino_api_response = requests.post(_casino_api_setbet_url, json=request_params_api)

		try:
			validate(instance=casino_api_response.json(), schema=bet_response_schema)
		except Exception, e:
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

		return casino_api_response.json()

	except Exception, err:
		self.retry(exc=err, countdown=2 ** self.request.retries)
