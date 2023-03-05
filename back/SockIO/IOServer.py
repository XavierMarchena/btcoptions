# -*- coding: UTF-8 -*
import eventlet
#from eventlet.green.OpenSSL import SSL
import os,sys,inspect
import sys



currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import socketio
import json
from Cache._cache import Cache

from BitcoinBet.main import process_win, format_balance_response, format_authenticate_response, format_bet_response
from BitcoinBet.btc_model import BtcRange
#from BitcoinBet.main import process_bet
from datetime import datetime, timedelta
#import time
from Core import bet_model
#from Core.bet_model import Players
#from Core.bet_model import Tokens
#from Core.players import save_player, update_player
#from Core.players import save_player, update_player
from Core import bet_controller
#from Core.bet_controller import save_player, update_player
#from Core import tokens

#from Api.leviathan_db import select_customer
from Api.main import bet, balance
import logging
import re
import decimal



sio = socketio.Server(cors_allowed_origins="*", logger=True, engineio_logger=True)
app = socketio.WSGIApp(sio)

_cach = Cache()
_transactions = bet_controller.Transactions()
_players = bet_controller.Players()
#_tokens = tokens.Tokens()


# def handleError(self, record):
#     raise
# logging.Handler.handleError = handleError


@sio.event
def connect(sid, environ):
	print('connect ', sid)

@sio.event
def my_message(sid, data):
	print('message ', data)

@sio.event
def disconnect(sid):
	print('disconnect ', sid)

@sio.on('btc_live_price')
def btc_live_price(sid):
	_event = 'btc_live_price'

	while True:
		try:
			_avg = float(_cach.GetCache('btc_avg'))
			sio.emit(_event, {'price': float("%.2f" % (_avg))}, room=sid)
			sio.sleep(1)
		except:
			print _avg
			sio.emit(_event, {'error': 500}, room=sid)


@sio.on('btc_range_price')
def btc_range_price(sid, data):
	_event = 'btc_range_price'
	try:
		_json = parse_data(data)
	except:
		sio.emit('btc_range_price', {'error':500}, room=sid)

	_rang = _json['range']
	_range = {0:{'hours':0, 'minutes':5,}, 1:{'hours':0, 'minutes':30}, 2:{'hours':1, 'minutes':0}, 3:{'hours':3, 'minutes':0}, 4:{'hours':6, 'minutes':0}, 5:{'hours':12, 'minutes':0}, 6:{'hours':24, 'minutes':0}}
	try:
		_select_range = _range[_rang]
	except:
		sio.emit(_event, {'error':500}, room=sid)

	_now = datetime.today()
	_bef = _now - timedelta(hours=_select_range['hours'], minutes=_select_range['minutes'])

	try:
		_result = BtcRange.objects.filter(date__gte=_bef, date__lte=_now).values_list("price", "date")
	except Exception as e:
		print str(e)

	_raw_result = []
	for _re in _result:
		_raw_result.append({'price':float(_re[0]), 'date':str(_re[1])})

	sio.emit(_event, {'range': _raw_result}, room=sid)




@sio.on('bets')
def bets(sid, data):
	_event = 'bets'
	try:
		_json = parse_data(data)
	except:
		sio.emit(_event, {'error':500}, room=sid)
		

	try:
		_idgame = _json['idgame']
		_token = _json['token']
		_betHistory = _json['betHistory']

		#_user_id = int(_json['userid'])
		#_desde = str(_json['desde'])
		#_hasta = str(_json['hasta'])
		#_len = int(_json['len'])
	except:
		sio.emit(_event, {'error':500}, room=sid)

	#_game = Games.objects.filter(id=_game_id)

	regex = re.compile('.*(%s).*' % _token)  # TODO FILTER WITH TOKEN AND IDGAME (GET PLATFORMID)

	_player = bet_model.Players.objects(tokens=regex)[0]

	if _betHistory == 'my':
		_bets = bet_model.Bets.objects(player_id=_player.player_id).order_by('-date').limit(10)
		#print 'my if'
		#print _bets
	elif _betHistory == 'all':
		_bets = bet_model.Bets.objects.order_by('-date').limit(10)
		#print 'all if'
		#print _bets
	else:
		#_betHistory == 'high':
		_bets = bet_model.Bets.objects.order_by('-amount_win', '-date').limit(10)
		#print 'high if'
		#print _bets


	_result = []

	for _bet in _bets:
		tmp_bet = {'date':str(_bet.date), 'bet':float(_bet.amount_bet), 'win':float(_bet.amount_win), 'profit': float(-_bet.amount_bet+ _bet.amount_win) if json.loads(_bet.result)["result"]!="tie" else float(0), 'result':json.loads(_bet.result)["result"]}
		_result.append(tmp_bet)


	sio.emit(_event, {'bets':_result}, room=sid)


def run_bet(_event,sid, _token, _currency, _balance, _bet_amount, _extras):
	if _balance < _bet_amount: #todo: check
	 	sio.emit(_event, {'error': 401, 'message': 'Not enough balance'}, room=sid)
		return {'result': 401}
	else:
		#TODO GET COUNTER VAR FOR USER
		for x in range(0, 11):#TODO: replace 11 with var
			sio.emit(_event, {'counter': int(10 - x)}, room=sid)
			sio.sleep(1)

		_process_win_result = process_win(_token, _currency, _balance, _bet_amount, _extras)

		return _process_win_result



@sio.on('make_bet')
def make_bet(sid, data):
	_event = 'make_bet'
	#_user_id = ""
	_balance = ""
	_bet_amount = ""
	_token = ""
	_extras = {}

	_win_amount = ""
	_result = ""

	try:
		#Parse data to json
		_json = parse_data(data)
	except:
		logging.fatal('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		sio.emit(_event, {'error':500, 'message': 'Error parsing data to json' }, room=sid)

	try:
		#Get vars from Frontend
		_profit_on_win = _json['profit_on_win']

		_bet_amount = _json['bet_amount']

		_extras = _json['extras']
		_token = _json['token']
		_homeurl = _json['homeurl']
		_round_id = _json['round_id']
		_currency = _json['currency']
		#_currency = _json['currency']
		_idgame = _json['idgame']
		#_client_id = _json['client_id']
		#_client_id = _json['client_id']

	except Exception,e:
		logging.fatal('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e) #todo: replace with logging
		sio.emit(_event, {'error':500, 'message': 'Error in frontend variables'}, room=sid)

	try:

		# Post Casino API
		request_params_front = {'token': _token, 'homeurl': _homeurl, 'currency': _currency, 'idgame':_idgame}

		_initial_balance = request_balance(request_params_front, _event, data,  sid)


		#PROCESS AND STORE IN GAME DB

		_run_bet_result = run_bet(_event, sid, _token, _currency, _initial_balance, _bet_amount, _extras)

		if _run_bet_result["result"]!=401:
			_transaction_id = _run_bet_result["transaction_id"]
			_win_amount = _run_bet_result["win_amount"]
			_result = _run_bet_result["result"]

			# _amount = _bet_amount - _win_amount

			try:
				request_params_front = {'token': _token, 'currency':_currency, 'amount': _win_amount, 'amount_win': _win_amount,
										'amount_bet': _bet_amount, 'homeurl': _homeurl, 'round_id': _round_id,
										'result': _result}

				logging.info(_transaction_id)
				request_bet(request_params_front, _transaction_id, _initial_balance, _result, _event, data, sid)
				# Final result

			except Exception, e:
				logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
				sio.emit(_event, {'error': 404, 'message': 'Casino API error'}, room=sid)
		else:
			sio.emit(_event, {'error': 401, 'message': 'Game error'}, room=sid)


	except Exception,e:
		logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		sio.emit(_event, {'error': 404, 'message': 'Casino API error'}, room=sid)

	#sio.emit(_event, _result, room=sid)
	# sio.emit(_event, {'error': 200, 'balance': _balance}, room=sid)


def request_bet(request_params_front, _transaction_id, _initial_balance, _result, _event, data,  sid):

	try:
		logging.info("Post /setBet to Casino API")
		# Post Casino API
		try:
			r = bet.delay(request_params_front)
			r = r.get(timeout=10)

			# if r['balance']: #TODO Replace r[balance] with STATUS CODE 200
			r = format_bet_response(r)

			_final_balance = r['balance']
			_casino_transaction_id = r['id_bet']

		except Exception,e:
			sio.emit(_event, {'error': 406, 'message': 'Casino API error'}, room=sid)
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


		try:
			_transaction = _transactions.save_transaction.delay(_casino_bet_id=str(_casino_transaction_id), _bet_id=str(_transaction_id), _type=str(_transactions.type_bet), _final_balance=float(_final_balance), _status=str(_transactions.status_success))
			_transaction = _transaction.get(timeout=10)
		except Exception,e:
			_transaction = _transactions.save_transaction.delay(_casino_bet_id=str(False),
																_bet_id=str(_transaction_id),
																_type=str(_transactions.type_bet),
																_final_balance=float(_initial_balance),
																_status=str(_transactions.status_failure))
			_transaction = _transaction.get(timeout=10)
			sio.emit(_event, {'error': 407, 'message': 'Game error'}, room=sid)
			logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

		#print _transaction

		sio.emit(_event, {'error': 200, 'balance': _final_balance}, room=sid)#todo:replace error with status
		sio.emit(_event, _result, room=sid)

	except Exception, e:

		sio.emit(_event, {'error': 408, 'message': 'Casino API error'}, room=sid)
		logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)



@sio.on('user_info')
def UserInfo(sid, data):
	"""

	:param sid:
	:param data:
	:return:
	"""
	_event = 'user_info'
	# _token = ''
	# _json = ''
	try:
		_json = parse_data(data)
		#TODO: Add json schema validator
	except:
		sio.emit(_event, {'error':500}, room=sid)

	try:

		#_client_id = _json['client_id']
		_token = _json['token']
		_idgame = _json['idgame']
		_lang = _json['lang']
		_currency = _json['currency']
		_homeurl = _json['homeurl']

	except:
		sio.emit(_event, {'error':500}, room=sid)

	try:

		# FrontEndData

		request_params_front = {'token': _token, 'homeurl':_homeurl, 'currency':_currency, 'idgame':_idgame}

		#POST TO CASINO OPERATOR AND PROCESS RESPONSE
		request_balance(request_params_front, _event, data, sid)


	except Exception, err:
		sio.emit(_event, {'error':401, 'message': err}, room=sid)


def request_balance(request_params_front, _event, data,  sid):

	#REQUEST TO CASINO API
	r = balance.delay(request_params_front)
	r = r.get(timeout=10)

	try:
		if r['balance']:#todo: GET STATUS CODE FROM RESPONSE 200, NOT FROM BALANCE

			r = format_balance_response(r)  # todo: format_balance_response

			_casino_player_id = r['userId']  # todo change var name
			_balance = r['balance']

			# SAVE GAME Internal DATA
			#GET PLATFORM_id with _idgame

			_idgame = request_params_front["idgame"]
			_platform_doc = bet_model.Platforms.objects.filter(idgame=_idgame)

			_player = bet_model.Players.objects.filter(casino_player_id=_casino_player_id) #TODO ADD TOKENS and PLATFORM filters
			if not _player:
				_player = _players.save_player.delay(casino_player_id=_casino_player_id, token=request_params_front["token"], currency=request_params_front["currency"], platform_id=_platform_doc[0].platform_id)
				_player = _player.get(timeout=10)
				#_player = Players.objects.filter(casino_player_id=_casino_player_id)
				#logging.info(_player)
			else:
				# TODO UPDATE_PLAYER TO SAVE TOKEN
				_player=_players.update_player.delay(casino_player_id=_casino_player_id, token=request_params_front["token"], currency=request_params_front["currency"], platform_id=_platform_doc[0].platform_id)
				_player = _player.get(timeout=10)
				#logging.info(_player)

			# SEND DATA TO FrontEnd
			sio.emit(_event, {'error': 200, 'balance': _balance, 'bet_multiplier': json.loads(_platform_doc[0].configuration)["bet_multiplier"], 'bet_min': json.loads(_platform_doc[0].configuration)["bet_min"], 'bet_max': json.loads(_platform_doc[0].configuration)["bet_max"] }, room=sid)
			#todo add bet_multiplier with platform_doc , 'bet_min': _platform_doc[0].configuration["bet_min"],'bet_max': _platform_doc[0].configuration["bet_max"]
			return _balance
		else:
			sio.emit(_event, {'error': 401, 'message': 'Casino API error'}, room=sid)

	except Exception, e:
		sio.emit(_event, {'error': 401, 'message': 'Casino API error'}, room=sid)
		logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)




def parse_data(data):
	_raw_data = {}
	for k, v in data.iteritems():
		if isinstance(k, unicode):
			if isinstance(v, unicode):
				_raw_data[str(k)] = str(v)
			else:
				_raw_data[str(k)] = v

	return _raw_data



if __name__ == '__main__':
	eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
	#eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('192.168.99.100', 5000)), certfile='/etc/ssl/certs/nginx-selfsigned.crt', keyfile='/etc/ssl/private/nginx-selfsigned.key', server_side = True), app)
	#eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('192.168.24.135', 5000)), certfile='cert.crt', keyfile='private.key', server_side = True), app)
	#pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler, keyfile='example.key', certfile='example.crt').serve_forever()