from extensions.socket import socketio
from flask_socketio import join_room
from flask import request
import os
from log_arbor.utils import log


def main_socket_events():

    '''
        Defines main events like joining
    '''

    @socketio.on("connect")
    def connect(auth):

        user_id = auth.get("user_id")

        log(os.getenv("LOGARBOR_AUTH_SERVICE_ID"), "info", f"user has joined the room: {user_id}", os.getenv("LOGARBOR_SUPPORT_TEAM_ACCESS_TOKEN"))

        if user_id:

            join_room(f"user_{user_id}")
