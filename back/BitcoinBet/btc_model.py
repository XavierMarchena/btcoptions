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
connect(_raw_mongo['db'], host=_raw_mongo['host'], port=_raw_mongo['port'], username=_raw_mongo['user'],
		password=_raw_mongo['pwd'], authentication_source="admin")


class BtcRange(Document):
	price = DecimalField(required=True, precision=2)
	date = DateTimeField(default=datetime.datetime.utcnow)