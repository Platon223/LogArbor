from flask_socketio import SocketIO
import os

socketio = SocketIO(async_mode="gevent", message_queue="redis://localhost:6379/0")