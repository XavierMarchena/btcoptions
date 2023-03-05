#!/usr/bin/env python
from __future__ import print_function
import os,sys,inspect
import json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


import pymysql


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
def select_customer(self,_client_id):
    conn = pymysql.connect(host=_raw_leviathan["leviathan_db_host"], port=3306, user=_raw_leviathan["leviathan_db_user"],
                           passwd=_raw_leviathan["leviathan_db_pwd"], db=_raw_leviathan["leviathan_db_name"])

    cur = conn.cursor()

    cur.execute("SELECT  `id`, `name`, `key`, `ip_list`, `balance_url`, `notification_url`, `disabled_at`, `created_at`, `updated_at`, `deleted_at` FROM `customers` LIMIT 1000")

    print(cur.description)

    print()
    customers = list()

    for row in cur:
        print(row)
        customers = {'CASINO_CLIENT_ID': row[0], 'CASINO_NAME': row[1], 'CASINO_API_SECRET': row[2], 'CASINO_API_BALANCE_URL': row[4], 'CASINO_API_NOTIFICATE_URL': row[5] }

    cur.close()
    conn.close()
    return json.dumps(customers)