# -*- coding: UTF-8 -*
import urllib
import hashlib
import json
from operator import itemgetter


def make_hash(_params, _secret):
	sign = hashlib.md5()
	sign.update(_params + _secret)
	return sign.hexdigest()

def verify_hash(_remote, _params, _secret):
	sign = hashlib.md5()
	print _secret
	sign.update(_params + _secret)
	print sign.hexdigest()
	return sign.hexdigest() == _remote


def encoded_params(dict_params):
	return urllib.quote(dict_params).encode('utf-8')

def encoded_dict(dict_params):
	return urllib.urlencode(dict_params).encode('utf-8')

def SockToken(_json):
	public_key = "444rgrtrtHH25"

	try:
		_time = int(_json['timestamp'])
		remote_token = str(_json['ApiToken'])
	except:
		return False

	_new_json = ""

	_final = len(_json) - 1
	count = 0

	for k, v in sorted(_json.items(), key=itemgetter(0)):
		if k != 'ApiToken':
			count += 1
			if count == _final:
				_new_json += "%s=%s" %(k, v)
			else:
				_new_json += "%s=%s&" %(k, v)

	if not verify_hash(remote_token, _new_json, public_key):
		return False

	return True








#def NewApiToken(f):
#	@functools.wraps(f)
#	def decorated_function(request, *args, **kws):
#
#		if request.method != "POST":
#			response = JsonResponse({'status':False, "message":"Method not allowed."}, status=403)
#			return response
#		
#		public_key = settings.NEW_API_PUBLIC
#		remote_token = request.META.get('HTTP_APITOKEN')
#		if remote_token is None:
#			return JsonResponse({'status':False,'message':'Unauthorized1'}, status=401)
#
#		cache_key = str(remote_token)
#		cache_time = 180
#
#		#if cache.get(cache_key):
#		#	return JsonResponse({'status':False, "message":"Unauthorizedhh"}, status=401)
#
#
#		try:
#			_raw_json = json.loads(request.body)
#			_time = int(_raw_json['timestamp'])
#		except:
#			return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)
#
#		_now_time = int(time.time())
#
#		_restart_time = _now_time - _time
#
#		#if _restart_time > 1:
#		#	return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)
#
#
#
#		_new_json = ""
#
#		_final = len(_raw_json)
#		count = 0
#		
#		for k, v in sorted(_raw_json.items(), key=itemgetter(0)):
#			count += 1
#			if count == _final:
#				_new_json += "%s=%s" %(k, v)
#			else:
#				_new_json += "%s=%s&" %(k, v)
#
#		#body = encoded_dict(json.loads(request.body))
#
#		if not verify_hash(remote_token, _new_json, public_key):
#			return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)
#
#		cache.set(cache_key, "hola", cache_time)
#
#		return f(request, *args, **kws)
#
#	return decorated_function