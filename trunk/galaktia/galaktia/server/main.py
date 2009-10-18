#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path
import sys

from twisted.internet import reactor
from twisted.python import log

from galaktia.protocol.base import BaseServer
from galaktia.protocol.controller import DispatcherController
from galaktia.protocol.model import SessionDAO
from galaktia.protocol.codec import ProtocolCodec

from galaktia.server.engines.engine import EngineResolver
from galaktia.server.persistence.dao import DAOResolver
from galaktia.server.persistence.orm import init_db

from galaktia.server.controllers.join import *
from galaktia.server.controllers.move import *
from galaktia.server.controllers.exit import *
from galaktia.server.controllers.talk import *

logger = logging.getLogger(__name__)

SERVER_VERSION = "0.2" # TODO: should be same as galaktia version, e.g.: 0.1.1

class GalaktiaServer(BaseServer):
    """ Implementation of the game server"""

    def __init__(self, session):
        self.session=session
            # Database session. Please, do not touch :P

        self.session_dao = SessionDAO()
        self.dao_resolver = DAOResolver(session)
        self.engine_resolver = EngineResolver(self.dao_resolver)

        controllers = {
                  'MoveDxDy': MoveDxDyController(self.session_dao, self.dao_resolver, self.engine_resolver),
                  'SayThis': SayThisController(self.session_dao, self.dao_resolver),
                  'RequestUserJoin': RequestUserJoinController(self.session_dao, self.dao_resolver),
                  'StartConnection': StartConnectionController(self.session_dao, self.dao_resolver),
                  'LogoutRequest': LogoutRequestController(self.session_dao, self.dao_resolver)
        }
        
        BaseServer.__init__(self, ProtocolCodec(self.session_dao), 
                            DispatcherController(controllers))

def get_session():
    here_dir = os.path.dirname(__file__)
    path = os.path.join(here_dir, '..', 'server', 'data', 'map.sqlite3')
    db_conn_str = 'sqlite:///%s' % path
    logger.info('Using database connection string: %s', db_conn_str)
    engine, metadata, session = init_db(db_conn_str)
    return session

def main(program, port=6414):
    """ Main program: Starts a server on given port """
    #log.startLogging(sys.stderr) # enables Twisted logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    protocol = GalaktiaServer(get_session())

    logger.info("Starting %s", "server")

    port = int(port)
    logger.info('Starting server at port: %d', port)
    reactor.listenUDP(port, protocol)
    reactor.run()
    logger.info('Stopped server')

if __name__ == '__main__':
    # print 'Usage: python -m galaktia.server.main [port]'
    main(*sys.argv)

