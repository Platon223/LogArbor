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

        print("user joined")