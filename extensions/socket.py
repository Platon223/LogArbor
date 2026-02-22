from flask_socketio import SocketIO
import os

redis_message_queue_socketio = os.getenv("REDIS_MESSAGE_QUEUE_SOCKETIO")

socketio = SocketIO(cors_allowed_origins="*", message_queue=redis_message_queue_socketio, async_mode="gevent")