#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os.path

import galaktia.server
from galaktia.server.persistence.orm import init_db
from galaktia.server.model.base import BaseServer
from galaktia.server.model.controller import DispatcherController
from galaktia.server.model.codec import JsonCodec
from galaktia.server.model.standalone import run_web_socket_server

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

    DEFAULT_DB_PATH = os.path.join(galaktia.server.__path__[0], \
            'data', 'map.sqlite3')

    def __init__(self, db_conn_str=None):
        # TODO XXX session = self._make_session(db_conn_str)
        codec = JsonCodec()
        controller = DispatcherController()
        super(GalaktiaServer, self).__init__(codec, controller)

    def _make_session(self, db_conn_str):
        if db_conn_str is None:
            db_conn_str = '/'.join(('sqlite://', self.DEFAULT_DB_PATH))
        logger.info('Using database connection string: %s', db_conn_str)
        engine, metadata, session = init_db(db_conn_str)
        return session

def main(program, host='', port=8880):
    """ Main program: Starts a server on given port """
    try:
        run_web_socket_server((host, int(port)), GalaktiaServer)
    except Exception:
        logger.exception('Failed to run server')
    except KeyboardInterrupt:
        logger.info('Stopped server')

if __name__ == '__main__':
    # print 'Usage: python -m galaktia.server.main [port]'
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main(*sys.argv)

