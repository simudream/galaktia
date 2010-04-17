#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Web socket handler for galaktia endpoint
"""

import logging
import os.path
import sys

from mod_pywebsocket import msgutil

from galaktia.server.persistence.orm import init_db
from galaktia.server.model.base import BaseServer
from galaktia.server.model.controller import DispatcherController
from galaktia.server.model.codec import JsonCodec

logger = logging.getLogger(__name__)

# We have a serious problem!!!
# There is 1 server instance for each web socket (each server on a
# different thread).
# We should use some kind of communicating singleton to be able to
# send messages to clients other than the one who sent the incoming
# requests.
# This is related to session management. There should be one web socket
# for each session and a way to retrieve them by session ID.

class GalaktiaServer(BaseServer):
    """ Galaktia web socket server implementation """

    DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), \
            'data', 'map.sqlite3')

    def __init__(self, db_conn_str=None):
        if db_conn_str is None:
            db_conn_str = '/'.join(('sqlite://', self.DEFAULT_DB_PATH))
        logger.info('Using database connection string: %s', db_conn_str)
        engine, metadata, session = init_db(db_conn_str)
        codec = JsonCodec()
        controller = DispatcherController(session) # TODO XXX session not arg
        super(GalaktiaServer, self).__init__(codec, controller)

_server = GalaktiaServer()
web_socket_do_extra_handshake = _server.handshake
web_socket_transfer_data = _server.run

## Web socket handler example:
#
# def web_socket_do_extra_handshake(request):
#     pass  # Always accept.
#
# def web_socket_transfer_data(request):
#     while True:
#         line = msgutil.receive_message(request)
#         msgutil.send_message(request, line)
#         if line == _GOODBYE_MESSAGE:
#             return

