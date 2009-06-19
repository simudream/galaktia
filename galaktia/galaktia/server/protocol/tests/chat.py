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
        return [(input_message+' server salted', (host, port))] 
                # extensible for more logic

user_list = []
class ManuServerProtocol(ChatServerProtocol):
    """ Implementation of basic chat server """
    
    #def __init__(self):
        
        #ChatServerProtocol.__init__(self)
        #super(self, ManuServerProtocol).__init__()
        
    
    def process(self, input_message, (host,port)):
        """ Implements processing by parsing input message"""
        dst = (host,port)
        parsed_input = input_message.split(':')
        if len(parsed_input) != 2 :
            return [("error:Message not understood",dst)]
        
        command, argument = parsed_input[0], parsed_input[1]
        
        if command == "new_user":
            if argument not in [x[0] for x in user_list]:
                user_list.append( [argument,dst] )
                logger.debug('New user @%s:%d: %s', host, port, argument)
                return [("user:accepted", (host,port))]
            else:
                return [("user:rejected",(host,port))]
        else:
            if command in [x[0] for x in user_list]:
                logger.debug('%s said %s' % (command,argument))
                lista = []
                for user_tuple in user_list:
                    lista.append((str(command+': '+argument), user_tuple[1]))
                return lista
            else:
                logger.error(str(parsed_input))
                


class ChatClientProtocol(BaseMessageProtocol):
    """ Implementation of a simple chat client (unreliable protocol) """

    DEFAULT_SERVER = '192.168.1.1'
    DEFAULT_PORT = 6414

    def __init__(self, server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """ ChatClientProtocol constructor """
        self.server = server
        self.port = int(port)

    def startProtocol(self):
        """ Triggers the first message sent by client on a session """
        self.transport.connect(self.server, self.port)
        sys.stdout.write('Connected to server %s\n' % self.server)
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
        if output_message == 'quit':
            return None # exits on empty message or by entering 'quit'
        return output_message

class ManuClientProtocol(ChatClientProtocol):
    username = ''
    
    def prompt_username(self):
        sys.stdout.write('Please enter your desired username. >>> ')
        my_username = raw_input()
        self.username = my_username
        return self.username
        
    def request_username_to_server(self, username):
        self.send("new_user:%s" % username)
    
    def startProtocol(self):
        """ Triggers the first message sent by client on a session """
        self.transport.connect(self.server, self.port)
        sys.stdout.write('Connected to server %s\n' % self.server)
        self.request_username_to_server(self.prompt_username())
        
    def process(self, input_message, (host,port)):
        """ Implements processing by parsing input message"""
        
        parsed_input = input_message.split(':')
        if len(parsed_input) != 2 :
            return [("error:Message not understood",dst)]
        
        command, argument = parsed_input[0], parsed_input[1]
        
        if command == "error":
            sys.stdout.write('Received error from server: %s', argument)
            return []
        elif command == "user":
            if argument == "accepted":
                sys.stdout.write("Username accepted by server :D")
                return []
            else:
                sys.stdout.write("Username rejected by server :(\n")
                return [("new_user:"+self.prompt_username(), None ) ]
        elif command == "aCommand":
            pass
        elif command == "otherCommand":
            pass
        else:
            sys.stdout.write(input_message)
            return []


        output_message = self.prompt()
        if output_message is None:
            reactor.stop() # the reactor singleton is not a good idea...
            return []
        return [(self.username+':'+output_message, None)]

def main(program, endpoint='client', host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    if endpoint == 'client':
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
        protocol = ChatClientProtocol(host, port)
        port = 0 # dinamically assign client port
    elif endpoint == 'server':
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        protocol = ChatServerProtocol()
    elif endpoint == 'mclient':
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
        protocol = ManuClientProtocol(host, port)
        port = 0 # dinamically assign client port
    elif endpoint == 'mserver':
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        protocol = ManuServerProtocol()
    else: # bad arguments
        print ('Usage: python %s [client|server|mclient|mserver]' + \
            ' [host] [port]') % program
        return
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)