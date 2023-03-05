import configparser
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

class Settings:
	def __init__(self):

		# if os.environ['ENV'] == 'TEST':
		# 	self.filename = "%s/Settings/settings.cfg" % (parentdir)
		# elif os.environ['ENV'] == 'DEVELOPMENT':
		# 	self.filename = "%s/Settings/settings_dev.cfg" % (parentdir)

		self.filename = "%s/Settings/settings.cfg" % (parentdir)
		self.config = configparser.RawConfigParser()
		self.config.read(self.filename)
		self.cache_ip = self.config.get('cache', 'ip')
		self.cache_port = self.config.get('cache', 'port')

		self.mongo_host = self.config.get('mongo', 'host')
		self.mongo_port = self.config.get('mongo', 'port')
		self.mongo_user = self.config.get('mongo', 'user')
		self.mongo_pwd = self.config.get('mongo', 'pwd')
		self.mongo_db = self.config.get('mongo', 'db')
		self.mongo_db1 = self.config.get('mongo', 'db1')
		self.mongo_db2 = self.config.get('mongo', 'db2')

		self.redis_broker_url = self.config.get('redis', 'broker_url')
		self.redis_backend_url = self.config.get('redis', 'backend_url')


	@property
	def get_cache(self):
		return {'ip':str(self.cache_ip), 'port':int(self.cache_port)}


	@property
	def get_mongo(self):
		return {'host':str(self.mongo_host), 'port':int(self.mongo_port), 'db':str(self.mongo_db), 'db1':str(self.mongo_db1), 'db2':str(self.mongo_db2), 'user':str(self.mongo_user), 'pwd':str(self.mongo_pwd)}

	@property
	def get_redis(self):
		return {'broker_url': str(self.redis_broker_url), 'backend_url': str(self.redis_backend_url)}

	# @property
	# def get_casino_api(self):
	# 	return {'casino_api_key': str(self.casino_api_key), 'casino_api_developer_id': str(self.casino_api_developer_id), 'casino_api_getbalance_url': str(self.casino_api_getbalance_url), 'casino_api_setbet_url': str(self.casino_api_setbet_url)}

	# @property
	# def get_leviathan(self):
	# 	return {'leviathan_db_host': str(self.leviathan_db_host), 'leviathan_db_user': str(self.leviathan_db_user), 'leviathan_db_pwd': str(self.leviathan_db_pwd), 'leviathan_db_name': str(self.leviathan_db_name)}


	#todo: encrypt/decrypt cfg
