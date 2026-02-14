from extensions.socket import socketio
from flask_socketio import join_room
from flask import request


def main_socket_events():

    '''
        Defines main events like joining
    '''

    @socketio.on("connect")
    def join_log_stream(auth):
        
        user_id = auth.get("user_id")

        if user_id:

            join_room(f"user_{user_id}")