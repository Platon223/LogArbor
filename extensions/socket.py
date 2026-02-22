from flask_socketio import SocketIO
import os

socketio = SocketIO(cors_allowed_origins="*", message_queue="redis://host.docker.internal:6379/2", async_mode="gevent")