from flask_socketio import SocketIO
import os

socketio = SocketIO(message_queue="redis://localhost:6379/0")