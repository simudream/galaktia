#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging
from random import randint

from twisted.internet import reactor
from twisted.python import log

from galaktia.server.protocol.model import Datagram, Message
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import Controller

from galaktia.server.protocol.operations.talk import *
from galaktia.server.protocol.operations.join import *

from galaktia.server.protocol.interface import ServerController


logger = logging.getLogger(__name__)

class CamelCaseChatServerController(ServerController):
    """ Implementation of a simple chat server """

    def __init__(self):
        self.sessions = dict()
        Controller.__init__(self)

    def on_say_this(self, talking_user, message):
        self.send_all(
              [SomeoneSaid(
                username = talking_user,
                message = message.title(), 
                host = self.sessions[aSession]['host'], 
                port = self.sessions[aSession]['port']) 
              for aSession in self.sessions ])
        
    def on_request_user_join(self, username):
            session_id = self._generate_session_id(username)
            if session_id not in self.sessions:
                self._create_session(session_id,username)
                self.send_all([UserAccepted(
                            host = self.host,
                            port = self.port,
                            accepted = True,
                            session_id = session_id,
                            player_initial_state = (randint(1,10),randint(1,10))
                            )
                        ] + \
                        [UserJoined(
                            username = username,
                            host = self.sessions[aSession]['host'],
                            port = self.sessions[aSession]['port']
                            )
                        for aSession in self.sessions])
            else:
                self.send( UserAccepted(
                            host = self.host,
                            port = self.port,
                            accepted = False
                            )
                        )
                
    def on_start_connection(self):
        self.send(
                   CheckProtocolVersion(
                    host = self.host,
                    port = self.port,
                    version = "0.1",
                    url = "http://www.galaktia.com.ar"
                    )
                  )
   

        
    def _generate_session_id(self,username):
        """ Assigns a unique identifier to the requested username """
        return str(username)
    
    def _create_session(self,session_id,username):
        self.sessions[session_id] = {
                'host' : self.host,
                'port' : self.port,
                'username' : username
                }


def main(program, endpoint='server', host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    class MockSession(object):
        def __init__(self, id):
            self.password = id
    class MockSessionDAO(object):
        def get(self, id):
            return MockSession(id)
    codec = ProtocolCodec(MockSessionDAO())
    log_level = logging.DEBUG
    controller = CamelCaseChatServerController()
    protocol = BaseServer(codec, controller)
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)
