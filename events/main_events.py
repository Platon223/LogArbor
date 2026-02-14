from extensions.socket import socketio
from flask_socketio import join_room
from flask import request


def main_socket_events():

    '''
        Defines main events like joining
    '''

    @socketio.on("connect")
    def join_log_stream():
        
        user_id = request.args.get("user_id")

        if user_id:

            join_room(f"user_{user_id}")