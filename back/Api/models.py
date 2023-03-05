# -*- coding: UTF-8 -*
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from mongoengine import *
import datetime
from Settings.settings import Settings


_sett = Settings()
_raw_mongo = _sett.get_mongo
connect(_raw_mongo['db1'], host=_raw_mongo['host'], port=_raw_mongo['port'], username=_raw_mongo['user'],
		password=_raw_mongo['pwd'], authentication_source="admin")

class Users(Document):
	username = StringField(max_length=50, required=True, primary_key=True)
	platform_name = StringField(max_length=50, required=True)


class Platforms(Document):
	name = StringField(max_length=50, required=True, primary_key=True)
	prefix = StringField(max_length=10, required=True)
	api_url = StringField(max_length=100, required=True)

class Coins(Document):
	name = StringField(max_length=50, required=True, primary_key=True)
	code = StringField(max_length=50, required=True)

class Credentials(Document):
	platform_name = StringField(max_length=50, required=True)
	platform_key = StringField(max_length=50, required=True)
	coin = StringField(max_length=50, required=True)

class Games(Document):
	name = StringField(max_length=50, required=True)
	category = StringField(max_length=50, required=True)

class Plays(Document):
	uu_id = StringField(max_length=80, required=True, primary_key=True)
	player = StringField(max_length=50, required=True)
	game = StringField(max_length=50, required=True)
	amount_bet = models.DecimalField(max_digits=16, decimal_places=6, blank=False,null=False)
	amount_win = models.DecimalField(max_digits=16, decimal_places=6, blank=False,null=False)
	extras = StringField(max_length=1000, required=True)



