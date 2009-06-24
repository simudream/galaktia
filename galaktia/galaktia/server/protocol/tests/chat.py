#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging
import simplejson

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

from baseChat import * # LOS IMPORTS CON * SON MALOS!!!

logger = logging.getLogger(__name__)


# ESTAS IMPLEMENTACIONES ESTARIAN MEJOR SI LAS HUBIERAMOS PENSADO ANTES

        
class ManuServerProtocol(ChatServerProtocol):
    """ Implementation of basic chat server """
    
    userList = []

    def process(self, input_message, (host,port)):
        """ Implements processing by parsing input message"""
        dst = (host,port)
        parsed_input = input_message.split(':')
        if len(parsed_input) != 2 :
            return [("error:Message not understood",dst)]
        
        command, argument = parsed_input[0], parsed_input[1]
        
        if command == "new_user":
            if argument not in [x[0] for x in self.userList]:
                self.userList.append( [argument,dst] )
                logger.debug('New user @%s:%d: %s', host, port, argument)
                return [("user:accepted", (host,port))]
            else:
                return [("user:rejected",(host,port))]
        else:
            if command in [x[0] for x in self.userList]:
                logger.debug('%s said %s' % (command,argument))
                lista = []
                for user_tuple in self.userList:
                    lista.append((str(command+': '+argument), user_tuple[1]))
                return lista
            else:
                logger.error(str(parsed_input))
                


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
        protocol = ManuClientProtocol(host, port)
        port = 0 # dinamically assign client port
    elif endpoint == 'server':
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
