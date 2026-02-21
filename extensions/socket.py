from flask_socketio import SocketIO
import os

socketio = SocketIO(cors_allowed_origins="*", message_queue="redis://127.0.0.1:6379/2", async_mode="gevent")