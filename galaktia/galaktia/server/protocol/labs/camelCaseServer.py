#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

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
    """ Implementation of a simple echo chat server """

    def process(self, input_message):
        """ Implements processing by returning output identical to input """
        command = input_message['name']
        if command == "SayThis":
            return [Message(text=input_message['text'].title(), \
                        host = input_message['host'], \
                        port = input_message['port']
                    )]
        elif command == "RequestUserJoin":
            user = input_message['username']
            return [Message(text="Hello %s, welcome to the CamelCase Server!" % user, \
                    host = input_message['host'], \
                    port = input_message['port']
                    )]
        else:
            raise ValueError, "Invalid command: %s" % command


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
