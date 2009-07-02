#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log


from galaktia.server.protocol.model import Datagram, Command
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import AcknowledgeController



logger = logging.getLogger(__name__)

class ClientController(AcknowledgeController):
    def greet(self):
        logger.info('Starting connection...')
        return [StartConection()]

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')

        #Talk commands
        if command == "SomeoneSaid":
            message = input_message['action']
            username = input_message['subject']
            self.on_chat(message, username)
        elif command == "UserAccepted":
            if input_message['accepted']:
                self.session_id = input_message['session_id']
                x, y = input_message['player_initial_state']
                self.on_user_accepted(x, y)
            else:                
                self.on_user_rejected()
        
        # Join commands
        elif command == "CheckProtocolVersion":
            version = input_message['version']
            url = input_message['url']
            self.on_version_received(version, url)
        elif command == "UserJoined":
            username = input_message['username']
            self.on_user_joined(username)
        elif command == None:
            self.acknowledged(input_message)

        else:
            raise ValueError, "Invalid command: %s" % command
        
        return []
            
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
    
class ServerController(AcknowledgeController):
    """ Implementation of a simple chat server """

    def __init__(self):
        self.sessions = dict()
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
            self.on_say_this(talking_user,message)
        elif command == "RequestUserJoin":
            username = input_message['username']
            self.on_request_user_join(username)
        elif command == "StartConection":
            self.on_start_connection()
        elif command == None:
            self.acknowledged(input_message)
        else:
            raise ValueError, "Invalid command: %s" % command
        return []
        
    def on_say_this(self, talking_user, message):
        raise NotImplementedError
    def on_request_user_join(self,username):
        raise NotImplementedError
    def on_start_connection(self):
        raise NotImplementedError
    
