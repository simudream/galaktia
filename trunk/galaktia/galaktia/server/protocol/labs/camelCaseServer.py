#!/usr/bin/env python
# -*- coding: utf-8 -*-

from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import Controller
from galaktia.server.protocol.interface import GalaktiaServer
from galaktia.server.protocol.model import Datagram, Message
from galaktia.server.protocol.operations.join import *
from galaktia.server.protocol.operations.talk import *
from random import randint
from twisted.internet import reactor
from twisted.python import log
import sys, logging






logger = logging.getLogger(__name__)

class CamelCaseChatServer(GalaktiaServer):
    """ Implementation of a simple chat server """

    def __init__(self):
        self.sessions = dict()
        self.host = None
        self.port = None
        GalaktiaServer.__init__(self)

    def on_say_this(self, talking_user, message):
        for aSession in self.sessions:
            self.someone_said(username = talking_user,
                message = message.title(), 
                host = self.sessions[aSession]['host'], 
                port = self.sessions[aSession]['port']) 

        
    def on_request_user_join(self, username):
            session_id = self._generate_session_id(username)
            if session_id not in self.sessions:
                self._create_session(session_id,username)
                for aSession in self.sessions:
                    self.user_joined( username = username,
                            host = self.sessions[aSession]['host'],
                            port = self.sessions[aSession]['port'])
                            
                self.user_accepted( host = self.host, port = self.port,
                        session_id = session_id,
                        player_initial_state = (randint(1,10),randint(1,10))
                        )
            else:
                self.user_rejected( host = self.host, port = self.port)

    def on_start_connection(self):
        self.check_protocol_version(host = self.host, port = self.port,
                    version="0.1", url="http://www.galaktia.com.ar")
   

        
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
    
    log_level = logging.DEBUG
    protocol = CamelCaseChatServer()
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

