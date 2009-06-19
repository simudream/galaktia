#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

import simplejson
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

logger = logging.getLogger(__name__)

class BaseMessageProtocol(DatagramProtocol):
    """ An abstract base class for remote object messaging """

    def datagramReceived(self, input_data, (host, port)):
        """ Event handler for datagram reception """
        input_message = self.decode(input_data)
        logger.debug('Received from %s:%d: %s', host, port, input_message)
        for output_message, dst in self.process(input_message, (host, port)):
            self.send(output_message, dst)

    def send(self, output_message, dst=None):
        """ Sends an output message to given destination (host, port) """
        self.transport.write(self.encode(output_message), dst)
        logger.debug('Sent to %s: %s', dst or 'server', output_message)

    def process(input_message, host, port):
        """ Processes input message (from host:port) into an output message """
        raise NotImplementedError

    def decode(self, input_data):
        """ Decompresses and deserializes input message data into an object """
        return simplejson.loads(input_data.decode('zlib'))

    def encode(self, output_message):
        """ Serializes and compresses an object into an output message data """
        return simplejson.dumps(output_message, \
                separators=(',', ':')).encode('zlib')

class ChatServerProtocol(BaseMessageProtocol):
    """ Implementation of a simple echo chat server """

    def process(self, input_message, (host, port)):
        """ Implements processing by returning output identical to input """
        return [(input_message, (host, port))] # extensible for more logic

class ChatClientProtocol(BaseMessageProtocol):
    """ Implementation of a simple chat client (unreliable protocol) """

    DEFAULT_SERVER = '127.0.0.1'
    DEFAULT_PORT = 6414

    def __init__(self, server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """ ChatClientProtocol constructor """
        self.server = server
        self.port = int(port)

    def startProtocol(self):
        """ Triggers the first message sent by client on a session """
        self.transport.connect(self.server, self.port)
        sys.stdout.write('Enter text to chat with the echo server')
        output_message = self.prompt()
        self.send(output_message or '')

    def connectionRefused(self):
        """ Event handler for refused connections (no server listening) """
        logger.error('No server listening at %s:%d', self.server, self.port)

    def process(self, input_message, (host, port)):
        """ Writes server response and prompts for a new message to send """
        sys.stdout.write(input_message)
        output_message = self.prompt()
        if output_message is None:
            reactor.stop() # the reactor singleton is not a good idea...
            return []
        return [(output_message, None)]

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
    if endpoint == 'client':
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
        protocol = ChatClientProtocol(host, port)
        port = 0 # dinamically assign client port
    elif endpoint == 'server':
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        protocol = ChatServerProtocol()
    else: # bad arguments
        print 'Usage: python %s [client|server] [host] [port]' % program
        return
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

