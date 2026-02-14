from flask_socketio import SocketIO
import os

socketio = SocketIO(message_queue="redis://redis-logarbor:6379/0")