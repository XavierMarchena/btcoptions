
import socketio

sio = socketio.Client(ssl_verify=True)

@sio.event
def connect():
	sio.emit('btc_live_price')
	print('connection established')

@sio.on('btc_live_price')
def my_message(data):
	print data
	print('message received with ', data)

@sio.event
def disconnect():
	print('disconnected from server')





sio.connect('https://socketio.rgtslots.com', transports="polling")
sio.wait()