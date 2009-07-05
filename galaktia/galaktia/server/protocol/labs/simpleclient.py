#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log

# should be using pyglet, but for this example it's ok
import pygame
from pygame.locals import *

from galaktia.server.protocol.model import Datagram, Command
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import Controller

from galaktia.server.protocol.operations.talk import *
from galaktia.server.protocol.operations.join import *

logger = logging.getLogger(__name__)

CLIENT_VERSION = "0.1"
SCREEN_SIZE = (800, 600)
pygame.init()
font = pygame.font.SysFont("arial", 16)
font_height = font.get_linesize()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
username = "Matias"
playerinLOS = []

class PygameClientController(Controller):
    def greet(self):

        pygame.display.set_caption("Simple Pygame Galaktia Client")
        self.event_text = ["Starting connection..."]
        return [StartConection()]

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')

        #Talk commands
        if command == None:
            # TODO: implement
            logger.info('received ACK: %s', input_message['ack'])
            return []
            
        elif command == "SomeoneSaid":
            string = input_message['action']
            self.event_text[-1] = input_message['subject'] + ": " + string
            self.event_text.append("Type to send chat")
            output_message = self.prompt()
            if output_message is None:
                reactor.stop() # the reactor singleton is not a good idea...
                return []
            return [SayThis(message=output_message, session_id = self.session_id)]
            
        elif command == "SayThisAck":
            output_message = self.prompt()
            if output_message is None:
                reactor.stop() # the reactor singleton is not a good idea...
                return []
            return [SayThis(message=output_message, session_id = self.session_id)]
            
        elif command == "UserAccepted":
            if input_message['accepted']:
                self.session_id = input_message['session_id']
                self.x,self.y = input_message['player_initial_state']
                return [UserAcceptedAck(ack = input_message['timestamp'])]
            else:
                self.event_text[-1] = "El server no acepta ese username."
                self.event_text.append("Type Other Username Please...")
                self.username = self.prompt()
                return [
                    UserAcceptedAck(ack = input_message['timestamp']),
                    RequestUserJoin(username = self.username)
                    ]
                
        elif command == "CheckProtocolVersion":
            version = input_message['version']
            if version != CLIENT_VERSION:
                self.event_text.append("Bajate la ultima version de: " + input_message['url'])
            else:
                self.event_text.append("Version "+ version)
            self.event_text.append("Type Your Username Please...")
            self.username = self.prompt()
            return [RequestUserJoin(username = self.username)]
            
        elif command == "UserJoined":
            if input_message['username'] == self.username:
                self.event_text[-1] = "Te has conectado."
            else:
                self.event_text.append("El usuario "+ input_message['username'] + " se ha conectado.")
            self.event_text.append("Type to send chat")
            output_message = self.prompt()
            if output_message is None:
                reactor.stop() # the reactor singleton is not a good idea...
                return []
            return [SayThis(message=output_message, session_id = self.session_id)]
            
        else:
            #self.event_text[-1] = string
            self.event_text.append("Type to send chat")
            self.event_text = self.event_text[-SCREEN_SIZE[1]/font_height:]
            output_message = self.prompt()
            if output_message is None:
                reactor.stop() # the reactor singleton is not a good idea...
                return []
            return [SayThis(message=output_message, session_id = self.session_id)]
        # raise ValueError, "Invalid command: %s" % command

    def prompt(self):
        """ Prompts to read a new message to be sent to the server """

        clock = pygame.time.Clock()
        input_string = ""
        keepGoing = True

        while keepGoing:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    reactor.stop()
                    return input_string
                elif event.type == KEYDOWN:
                    key = event.key
                    if key == K_RETURN:
                        keepGoing = False
                    elif key == K_BACKSPACE:
                        input_string = input_string[:-1]
                    else:
                        try:
                            input_string += chr(event.key)
                        except:
                            pass
                    self.user_is_typing(input_string)
            screen.fill((255, 255, 255))
            pygame.draw.line(screen, (0,0,0),(0,SCREEN_SIZE[1]-font_height-1),\
                       (SCREEN_SIZE[0],SCREEN_SIZE[1]-font_height-1),1)
            y = SCREEN_SIZE[1]-font_height
            for text in reversed(self.event_text):
                screen.blit( font.render(text, True, (0, 0, 0)), (0, y) )
                y-=font_height
            pygame.display.flip()

        output_message = input_string
        if output_message == 'quit':
            return None # exits on empty message or by entering 'quit'
        return output_message
        
    def user_is_typing(self, string):
        self.event_text[-1] = string

def main(program, endpoint='client', host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    class MockSession(object):
        def __init__(self, id):
            self.id = id
        def get_encryption_key(self):
            return self.id
    class MockSessionDAO(object):
        def get(self, id):
            return MockSession(id)
    codec = ProtocolCodec(MockSessionDAO())

    log_level = logging.DEBUG
    controller = PygameClientController()
    protocol = BaseClient(codec, controller, host, port)
    port = 0 # dinamically assign client port
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting %s', endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

