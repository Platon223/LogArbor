from flask_socketio import SocketIO
import os

socketio = SocketIO(async_mode="eventlet", message_queue="redis://localhost:6379/0")