# -*- coding: UTF-8 -*
import os,sys,inspect



currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import time
import logging
import re
import json

from Cache._cache import Cache
from Core.bet_controller import Bets
from Core.bet_model import Platforms, Players

_bets = Bets()
_cach = Cache()

def process_bet(_tipo, _superbet, _bet_price):
	"""
	Call from this file, calculate bet result

	:param _tipo: 'higher' 1 'lower' 0
	:param superbet: True False
	:param _bet_price: Num
	:return:
	"""
	try:
		# definir el cobro de la apuesta al jugador

		_price_result = None

		_win_superbet = False

		_live_price = float(_cach.GetCache('btc_avg'))

		if _bet_price < _live_price:
			_price_result = "higher"  # 1 #higher
		elif _bet_price > _live_price:
			_price_result = "lower"  # 0 #lower
		else:
			_price_result = 2  # tie

		# print _price_result

		if _price_result != 2:
			if _tipo == _price_result:
				#_win = True
				_result = 'win'
				_diff = abs(_bet_price - _live_price)
				if _diff >= 10.00 and _superbet:#todo or remove
					_win_superbet = True
			else:
				_result = 'lose'
		else:
			#_tie = True
			_result= 'tie'

		_result = {'result': _result, 'price_result': _live_price} #todo: change win-tie to result:win/tie/lose

		return _result

	except Exception,e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)



def process_win(_token, _currency, _balance,_amount,_extras):
	"""
	Call from IOserver
	:param _token:
	:param _balance:
	:param _amount:
	:param _extras:
	:return:
	"""
	try:
		if _balance >= _amount:
			_tipo = _extras['type']
			_superbet = int(_extras['superbet'])
			_bet_price = float(_extras['btc_price'])

		_result = process_bet(_tipo, _superbet, _bet_price)

		if _result['result'] == 'win':
			#_amount_win = float(_amount ) * 100
			#TODO GET PLATFORM WITH PLAYER AND GET PLAYER WITH TOKEN
			regex = re.compile('.*(%s).*' % _token)  # TODO ADD CURRENCY FILTER
			# _bet_uuid = uuid.uuid1().hex
			# _token = Tokens.objects.filter(token=token)
			_player_doc = Players.objects(tokens=regex)  # TODO ADD CURRENCY FILTER

			_platform_doc = Platforms.objects.filter(platform_id=_player_doc[0].platform_id)
			#print (json.loads(_platform_doc[0].configuration))

			_bet_multiplier = json.loads(_platform_doc[0].configuration)["bet_multiplier"]
			#logging.info(_bet_multiplier)

			_amount_win = _amount  * _bet_multiplier
			#_amount_win = float(_amount)  * 1.5
		else:
			if _result['result'] == 'tie':
				_amount_win = 0
			else:
				_amount_win = 0

		#
		# Return data to Socket

		#_transaction_id = _bets.save_bet.delay(_token, _currency, "BBET", _amount, _amount_win, _balance, _extras, _result)  # TODO:Game ID from configGam
		_bet = _bets.save_bet.delay(_token, _currency, "BBET", _amount, _amount_win, _balance, _extras, _result)  # TODO:Game ID from configGam
		_transaction_id = _bet.get(timeout=10)
		logging.info(_transaction_id)
		#_transaction_id = _bet_doc[0].bet_id
		_result_dict = {'win_amount': _amount_win,
						'result': _result,
						'transaction_id': _transaction_id}
		return _result_dict


	except Exception, e:
		logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def format_authenticate_response(r):
	r["balance"] = round(float(r["balance"]),3)
	return r

def format_balance_response(r):
	r["balance"] = round(float(r["balance"]),3)
	return r

def format_bet_response(r):
	r["balance"] = round(float(r["balance"]),3)
	return r

