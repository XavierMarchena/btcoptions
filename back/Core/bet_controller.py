import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import bet_model
import uuid
import json
import re
import logging
from enum import Enum
from celery import Celery
from Settings.settings import Settings

# from mongoengine.queryset.visitor import Q

_sett = Settings()
_raw_redis = _sett.get_redis

# BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = _raw_redis['broker_url']
# BACKEND_URL = 'redis://localhost:6379/1'
BACKEND_URL = _raw_redis['backend_url']

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL, include=["Api.main"])
# app.add_defaults({
#     'CELERYD_HIJACK_ROOT_LOGGER': False,
# })


class Transactions():
    # STATUS_VALID="valid"
    # STATUS_INVALID = "invalid"
    # STATUS_REFUND = "refund"

    def __init__(self):
        self.type_bet = "bet"
        # self.status_invalid = "invalid"
        self.type_refund = "refund"
        self.status_success = "success"
        self.status_failure = "failure"

    @app.task(bind=True, max_retries=3, name='Core.bet_controller.save_transaction')
    def save_transaction(_self, _casino_bet_id, _bet_id, _type, _final_balance, _status):
        try:
            _transaction = bet_model.Transactions(casino_bet_id=_casino_bet_id, bet_id=_bet_id, type=_type,
                                                  final_balance=_final_balance, status=_status)
            logging.info(_bet_id)
            _transaction.save()
        except Exception, err:
            _self.retry(exc=err, countdown=2 ** _self.request.retries)


class Players():

    def __init__(self):
        # self.type_bet = "bet"
        # self.status_invalid = "invalid"
        self.type = "NotImplemented"

    @app.task(bind=True, max_retries=3, name='Core.bet_controller.save_player')
    def save_player(_self, casino_player_id, token, currency, platform_id):
        try:
            _uuid = str(uuid.uuid4())

            _tokens = {}
            _tokens[currency] = token
            _player = bet_model.Players(player_id=_uuid, casino_player_id=casino_player_id, platform_id=platform_id,
                                        tokens=json.dumps(_tokens))
            _player.save()
            logging.info(_player)


        except Exception, err:
            _self.retry(exc=err, countdown=2 ** _self.request.retries)

    @app.task(bind=True, max_retries=3, name='Core.bet_controller.update_player')
    def update_player(_self, casino_player_id, token, currency, platform_id):
        try:
            # todo
            _player = bet_model.Players.objects.filter(casino_player_id=casino_player_id, platform_id=platform_id)
            _tokens = json.loads(_player[0].tokens)

            _tokens[currency] = token
            logging.info(_tokens)
            # _player[0].tokens = _tokens
            _player[0].update(tokens=json.dumps(_tokens))
            logging.info(_player[0])
            # todo:get token json and update tokens
            # return _player
        except Exception, err:
            _self.retry(exc=err, countdown=2 ** _self.request.retries)


class Bets():
    # STATUS_VALID="valid"
    # STATUS_INVALID = "invalid"
    # STATUS_REFUND = "refund"

    def __init__(self):
        # self.type_bet = "bet"
        # self.status_invalid = "invalid"
        self.type_refund = "refund"

    @app.task(bind=True, max_retries=3, name='Core.bet_controller.save_bet')
    def save_bet(_self, _token, _currency, game_id, amount_bet, amount_win, balance, extra, result):
        """

        :param casino_player_id:
        :param game_id:
        :param amount_bet:
        :param amount_win:
        :param extra:
        :param result:
        :return:
        """
        try:
            regex = re.compile('.*(%s).*' % _token) #TODO FILTER WITH TOKEN AND game_id
            #_bet_uuid = uuid.uuid1().hex
            _bet_uuid = str(uuid.uuid4())
            # _token = Tokens.objects.filter(token=token)
            _player = bet_model.Players.objects(tokens=regex)[0]

            _bet = bet_model.Bets(bet_id=_bet_uuid, player_id=_player.player_id, amount_bet=amount_bet,
                                  amount_win=amount_win, initial_balance=balance, extra=json.dumps(extra),
                                  result=json.dumps(result), currency=_currency)
            _bet.save()
            #return json.dumps(_bet)
            return _bet_uuid
        except Exception, err:
            _self.retry(exc=err, countdown=2 ** _self.request.retries)
