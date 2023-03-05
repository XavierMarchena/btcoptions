# -*- coding: UTF-8 -*
import os,sys,inspect
import json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


from mysql_helper import MysqlPython

from Settings.settings import Settings
from celery import Celery

_sett = Settings()
_raw_leviathan = _sett.get_leviathan

_sett = Settings()
_raw_redis = _sett.get_redis


BROKER_URL = _raw_redis['broker_url']

BACKEND_URL = _raw_redis['backend_url']

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL, include=["Api.main"])

@app.task(bind=True, max_retries=3, name='Api.leviathan_db.selectcustomer')
def select_customer(self, client_id):
	try:
		connect_mysql = MysqlPython(_raw_leviathan["leviathan_db_host"], _raw_leviathan["leviathan_db_user"],
									_raw_leviathan["leviathan_db_pwd"],
									_raw_leviathan["leviathan_db_name"])
		print connect_mysql
		result = connect_mysql.select('id', 'name', 'key', 'ip_list', 'balance_url', 'notification_url', 'disabled_at',
									  'created_at', 'updated_at', 'deleted_at', id=client_id)
		print result

		return result


	except Exception, err:
		self.retry(exc=err, countdown=2 ** self.request.retries)