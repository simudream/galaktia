#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log


from galaktia.server.protocol.model import Datagram, Command
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import Controller

from galaktia.server.protocol.operations.talk import *
from galaktia.server.protocol.operations.join import *

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
                x,y = input_message['player_initial_state']
                self.on_user_accepted(x,y)
            else:
                self.on_user_rejected()
        
        # Join commands
        elif command == "CheckProtocolVersion":
            version = input_message['version']
            url = input_message['url']
            self.on_version_received(version,url)
        elif command == "UserJoined":
            username = input_message['username']
            self.on_user_joined(username)
        elif command == None:
            ack_id = input_message['ack']
            self.acknowledged(ack_id)
            logger.info('received ACK: %s', ack_id)

        else:
            raise ValueError, "Invalid command: %s" % command
        
        return []
            
    def on_chat(self, message, username):
        raise NotImplementedError
    def on_user_accepted(self,x,y):
        raise NotImplementedError
    def on_user_rejected(self):
        raise NotImplementedError
    def on_version_received(self,version,url):
        raise NotImplementedError
    def on_user_joined(username):
        raise NotImplementedError
