from flask_socketio import SocketIO
import os

redis_message_queue_socketio = os.getenv("REDIS_MESSAGE_QUEUE_SOCKETIO", "redis://127.0.0.1:6379/3")

socketio = SocketIO(cors_allowed_origins="*", message_queue=redis_message_queue_socketio, async_mode="gevent")