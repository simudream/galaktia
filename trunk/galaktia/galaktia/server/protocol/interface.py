#!/usr/bin/python
# -*- coding: utf-8 -*-

from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import AcknowledgeController
from galaktia.server.protocol.model import Datagram, Command
from pyglet.event import EventDispatcher
from twisted.internet import reactor
from twisted.python import log
import sys, logging


logger = logging.getLogger(__name__)


class GalaktiaClientController(EventDispatcher):
    def greet(self):
        self.dispatch_events('on_greet')

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')
        
        
        # TODO: if-elses and switch-cases are for loser languages,
        # mapping is better
        #Talk commands
        if command == "SomeoneSaid":
            message = input_message['action']
            username = input_message['subject']
            self.dispatch_events('on_chat', username, message)
        elif command == "UserAccepted":
            if input_message['accepted']:
                self.session_id = input_message['session_id']
                x, y = input_message['player_initial_state']
                self.dispatch_events('on_user_accepted', username, message)
            else:                
                self.dispatch_events('on_user_rejected')
        
        # Join commands
        elif command == "CheckProtocolVersion":
            version = input_message['version']
            url = input_message['url']
            self.dispatch_events('on_check_protocol_version', version, url)

        elif command == "UserJoined":
            username = input_message['username']
            self.dispatch_events('on_user_joined', username)
        elif command == None:
            self.acknowledged(input_message)

        else:
            raise ValueError, "Invalid command: %s" % command
        
        return [input_message.acknowledge()]


GalaktiaClientController.register_event_type('on_chat')
GalaktiaClientController.register_event_type('on_user_accepted')
GalaktiaClientController.register_event_type('on_user_rejected')
GalaktiaClientController.register_event_type('on_version_received')
GalaktiaClientController.register_event_type('on_user_joined')


class GalaktiaClient(BaseClient):
    """ Convenience client interface """
    def __init__(self):
        BaseClient.__init__(self, ProtocolCodec(), GalaktiaClientController())
        self.session_id = None
        self.controller.push_handlers(self)
    
    # Event Handlers
    # Already implemented
    def on_greet(self):
        self.start_connection()

    # To be implemented by class user
    def on_chat(self, message, username):
        raise NotImplementedError
    def on_user_accepted(self, x, y):
        raise NotImplementedError
    def on_user_rejected(self):
        raise NotImplementedError
    def on_version_received(self, version, url):
        raise NotImplementedError
    def on_user_joined(username):
        raise NotImplementedError
    
    
    # Convinience protocol methods
    def start_connection(self):
        logger.info('Starting connection...')
        return [StartConection()]
    def request_user_join(self,username):
        self.send(RequestUserJoin(username = username))
    def say_this(self,message):
        m = SayThis(message=message, session_id = self.session_id)
        self.send(m)
    
   
    
    
class ServerController(EventDispatcher):
    """ Implementation of a simple chat server """

    def __init__(self):
        self.host = None
        self.port = None
        AcknowledgeController.__init__(self)

    def process(self, input_message):
        """ Implements processing by returning CamelCased input 
            Please see protocol specification for more on messages
        """
        command = input_message.get('name')

        self.host = input_message.host
        self.port = input_message.port

        if command == "SayThis":
            talking_user = input_message['subject']
            message = input_message['action']
            self.dispatch_events('on_say_this', talking_user, message)
            return self.on_say_this(talking_user, message)
        elif command == "RequestUserJoin":
            username = input_message['username']
            return self.on_request_user_join(username)
        elif command == "StartConection":
            return self.on_start_connection()
        elif command == None:
            return self.acknowledged(input_message)
        raise ValueError("Invalid command: %s" % command)

    def on_say_this(self, talking_user, message):
        raise NotImplementedError
    def on_request_user_join(self, username):
        raise NotImplementedError
    def on_start_connection(self):
        raise NotImplementedError

ServerController.register_event('on_say_this')









