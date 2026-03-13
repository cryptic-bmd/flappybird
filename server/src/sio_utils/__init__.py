from src.sio_utils.extended import ExtendedSocket

socketio_object = ExtendedSocket()
sio = socketio_object.sio
socketio_app = socketio_object.socketio_app
