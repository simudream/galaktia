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

from galaktia.server.protocol.operations.talk import SayThis
from galaktia.server.protocol.operations.join import RequestUserJoin


logger = logging.getLogger(__name__)

class CamelCaseChatServerController(Controller):
    """ Implementation of a simple chat server """

    def __init__(self):
        self.sessions = dict()
        Controller.__init__(self)

    def process(self, input_message):
        """ Implements processing by returning CamelCased input 
            Please see protocol specification for more on messages
        """
        command = input_message['name']
        if command == "SayThis":
            talking_user = input_message['subject']
            return [SomeoneSaid(
                        username = talking_user,
                        message = input_message['action'].title(), 
                        host = self.sessions[aSession]['host'], 
                        port = self.sessions[aSession]['port']
                    ) for aSession in self.sessions ]
        elif command == "RequestUserJoin":
            username = input_message['username']
            session_id = self._generate_session_id(username)
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                            'host' : input_message['host'],
                            'port' : input_message['port'],
                            'username' : username
                            }
                return [UserAccepted(
                            host = self.sessions[session_id]['host'],
                            port = self.sessions[session_id]['port'],
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
                        for aSession in self.sessions]
            else:
                return [UserAccepted(
                            host = self.sessions[session_id]['host'],
                            port = self.sessions[session_id]['port'],
                            accepted = False,
                            )
                        ]
        elif command == "StartConection":
            return [ CheckProtocolVersion(
                        version = "0.1",
                        url = "http://www.galaktia.com.ar"
                        )
                    ]
        elif command == "UserAcceptedAck":
            # TODO: implement
            return []
        else:
            raise ValueError, "Invalid command: %s" % command
        
    def _generate_session_id(username):
        """ Assigns a unique identifier to the requested username """
        return username


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
