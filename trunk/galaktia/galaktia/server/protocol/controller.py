#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log

from galaktia.server.protocol.model import Datagram, Message
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec

logger = logging.getLogger(__name__)

class Controller(object):

    def greet(self):
        """ Returns Message objects to be sent to start a connection """
        return [] # override in clients to start a connection

    def process(self, input_message):
        """ Returns an iterable of output messages in response to input """
        raise NotImplementedError

class EchoChatServerController(Controller):
    """ Implementation of a simple echo chat server """

    def process(self, input_message):
        """ Implements processing by returning output identical to input """
        return [input_message]

class ChatClientController(Controller):

    def greet(self):
        sys.stdout.write('Enter text to chat with the echo server')
        output_message = self.prompt()
        return [Message(text=output_message)]

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        sys.stdout.write(input_message.get('text', '?'))
        output_message = self.prompt()
        if output_message is None:
            reactor.stop() # the reactor singleton is not a good idea...
            return []
        return [Message(text=output_message)]

    def prompt(self):
        """ Prompts to read a new message to be sent to the server """
        sys.stdout.write('\n> ')
        output_message = sys.stdin.readline() # prompts user for input
        output_message = output_message.rstrip('\n')
        if not output_message or output_message == 'quit':
            return None # exits on empty message or by entering 'quit'
        return output_message

def main(program, endpoint='client', host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    class MockSession(object):
        def __init__(self, id):
            self.password = id
    class MockSessionDAO(object):
        def get(self, id):
            return MockSession(id)
    codec = ProtocolCodec(MockSessionDAO())
    if endpoint == 'client':
        log_level = logging.INFO
        controller = ChatClientController()
        protocol = BaseClient(codec, controller, host, port)
        port = 0 # dinamically assign client port
    elif endpoint == 'server':
        log_level = logging.DEBUG
        controller = EchoChatServerController()
        protocol = BaseServer(codec, controller)
    else: # bad arguments
        print 'Usage: python %s [client|server] [host] [port]' % program
        return
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

