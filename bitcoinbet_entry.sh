#!/bin/sh
/usr/bin/supervisord -c /etc/supervisord.conf
redis-server
cd /bitcoinbet/back/Api
celery worker --loglevel=info -A main