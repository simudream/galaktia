#!/usr/bin/python
# -*- coding: utf-8 -*-

from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec
from galaktia.server.protocol.controller import Controller
from galaktia.server.protocol.model import Datagram, Command
from pyglet.event import EventDispatcher
from twisted.internet import reactor
from twisted.python import log
import sys, logging

from galaktia.server.protocol.operations.talk import *
from galaktia.server.protocol.operations.join import *


logger = logging.getLogger(__name__)




class GalaktiaClientController(EventDispatcher, Controller):
    def greet(self):
        self.dispatch_events('on_greet')

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')
        
        if command == None:
            self.dispatch_events('on_acknowledge', input_message['ack'])
            return []
        
        # TODO: if-elses and switch-cases are for loser languages,
        # mapping is better
        #Talk commands
        if command == "PlayerEnteredLOS":
            session_id = input_message['subject']
            (x,y) = input_message['object']
            description = input_message['description']
            self.dispatch_events('on_player_entered_los',
                     session_id, (x,y), description )
        elif command == "PlayerMoved":
            other_session_id = input_message["subject"]
            (dx, dy) = input_message["action"]
            (x,y) = input_message["subject"]
            self.dispatch_events('on_player_moved',
                     other_session_id, (dx,dy), (x,y))
        elif command == "SomeoneSaid":
            message = input_message['action']
            username = input_message['subject']
            self.dispatch_events('on_someone_said', username, message)
        elif command == "UserAccepted":
            if input_message['accepted']:
                self.session_id = input_message['session_id']
                x, y = input_message['player_initial_state']
                self.dispatch_events('on_user_accepted', session_id, (x,y))
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
        
        # Exit Commands
        elif command == "LogoutResponse":
            self.dispatch_events('on_logout_response')
        elif command == "UserExited":
            session_id = input_message['subject']
            self.dispatch_events('on_user_exited', session_id)
        else:
            raise ValueError, "Invalid command: %s" % command
        
        return [input_message.acknowledge()]

GalaktiaClientController.register_event_type('on_acknowledge')

GalaktiaClientController.register_event_type('on_player_entered_los')
GalaktiaClientController.register_event_type('on_player_moved')
GalaktiaClientController.register_event_type('on_someone_said')
GalaktiaClientController.register_event_type('on_user_accepted')
GalaktiaClientController.register_event_type('on_user_rejected')
GalaktiaClientController.register_event_type('on_check_protocol_version')
GalaktiaClientController.register_event_type('on_user_joined')
GalaktiaClientController.register_event_type('on_logout_response')
GalaktiaClientController.register_event_type('on_user_exited')


class ClientProtocolInterface(BaseClient):
    """ Convenience client interface """
    def __init__(self):
        class MockSession(object):
            def __init__(self, id):
                self.id = id
            def get_encryption_key(self):
                return self.id
        class MockSessionDAO(object):
            def get(self, id):
                return MockSession(id)
        BaseClient.__init__(self, ProtocolCodec(MockSessionDAO()),
                             GalaktiaClientController())
        self.session_id = None
        self.controller.push_handlers(self)
    
    # Event Handlers
    # Already implemented
    def on_greet(self):
        self.start_connection()

    # To be implemented by class user
    def on_player_entered_los(self, session_id, (x,y), description):
        raise NotImplementedError
    def on_someone_said(self, message, username):
        raise NotImplementedError
    def on_user_accepted(self, session_id, (x, y)):
        raise NotImplementedError
    def on_user_rejected(self):
        raise NotImplementedError
    def on_version_received(self, version, url):
        raise NotImplementedError
    def on_user_joined(self, username):
        raise NotImplementedError
    def on_logout_response(self):
        raise NotImplementedError
    def on_user_exited(self, session_id):
        raise NotImplementedError
    
    
    # Convinience protocol methods
    def move_dx_dy(self,(dx,dy)):
        m = MoveDxDy(session_id = self.session_id, delta = (dx,dy))
        self.send(m)
    def say_this(self,message):
        m = SayThis(message=message, session_id = self.session_id)
        self.send(m)
    def request_user_join(self,username):
        self.send(RequestUserJoin(username = username))
    def start_connection(self):
        logger.info('Starting connection...')
        self.send(StartConection())
    def logout_request(self):
        self.send(LogoutRequest(session_id = self.session_id))
    
    
    
    
   
    
    
class GalaktiaServerController(EventDispatcher, Controller):
    """ Implementation of a simple chat server """

    def process(self, input_message):
        """ Implements processing by returning CamelCased input 
            Please see protocol specification for more on messages
        """
        command = input_message.get('name')

        if command == "Acknowledge":
            self.dispatch_events('on_acknowledge', input_message['ack'])
            return []
        
        
        if command == "MoveDxDy":
            session_id = input_message['subject']
            (dx, dy) = input_message['action']
            self.dispatch_events('on_move_dx_dy', session_id, (dx,dy))
        elif command == "SayThis":
            talking_user = input_message['subject']
            message = input_message['action']
            self.dispatch_event('on_say_this', talking_user, message)

        elif command == "RequestUserJoin":
            username = input_message['username']
            self.dispatch_event('on_request_user_join', username)
        elif command == "StartConection":
            host = input_message.host
            port = input_message.port
            self.dispatch_event('on_start_connection', (host,port))
        elif command == "LogoutRequest":
            session_id = input_message['session_id']
            self.dispatch_event('on_logout_request', session_id)
        else:
            raise ValueError("Invalid command: %s" % command)
        
        #should return [input_message.acknowledge()]
        return []

GalaktiaServerController.register_event_type('on_acknowledge')

GalaktiaServerController.register_event_type('on_move_dx_dy')
GalaktiaServerController.register_event_type('on_say_this')
GalaktiaServerController.register_event_type('on_request_user_join')
GalaktiaServerController.register_event_type('on_start_connection')
GalaktiaServerController.register_event_type('on_logout_request')


class ServerProtocolInterface(BaseServer):
    """ Convenience server interface """
    
    #Overrides
    def __init__(self):

        self.sessions = {}
        class MockSession(object):
            def __init__(self, id):
                self.id = id
            def get_encryption_key(self):
                return self.id
        class MockSessionDAO(object):
            def get(self, id):
                return MockSession(id)

        BaseServer.__init__(self, ProtocolCodec(MockSessionDAO()), 
                            GalaktiaServerController())
        self.controller.push_handlers(self)
        
    def datagramReceived(self, input_data, (host, port)):
        self.host = host
        self.port = port
        BaseServer.datagramReceived(self, input_data, (host, port))

    def on_acknowledge(self, ack):
        #TODO: implement
        pass
    
    # Event Handlers
    # To be implemented by class user

    def on_move_dx_dy(self, session_id, (dx,dy)):
        raise NotImplementedError
    def on_say_this(self, talking_user, message):
        raise NotImplementedError
    def on_request_user_join(self, username):
        raise NotImplementedError
    def on_start_connection(self, (host,port) ):
        raise NotImplementedError
    def on_logout_request(self, session):
        raise NotImplementedError
    
  
    # Convinience protocol methods
    def player_entered_los(self, session_id, position, description):
        m = PlayerEnteredLOS(session_id = session_id,
                             position = position,
                             description = description
                             )
        self.send(m)
    def player_moved(self, (dx,dy), (x,y)):
        m = PlayerMoved(session_id = self.session_id,
                        delta = (dx,dy),
                        position=(x,y))
        self.send(m)
    
    def someone_said(self, host, port, username, message):
        self.send(SomeoneSaid(
            username = username,
            message = message, 
            host = host, 
            port = port))
            

    def user_accepted(self, host, port, session_id, player_initial_state):
        self.send(UserAccepted( host = host, port = port,
                            accepted = True, session_id = session_id,
                            player_initial_state = player_initial_state
                            ))
        
    def user_rejected(self, host, port):
        self.send(UserAccepted( host = host, port = port,
                            accepted = False)
                            )
    def check_protocol_version(self, host, port, version, url):
        self.send(CheckProtocolVersion(host = host, port = port,
                    version=version, url=url))
    def user_joined(self, session_id, username):
        self.send(UserJoined( username = username,
                    host = self.sessions[session_id][host],
                    port = self.sessions[session_id][port]))
    
    def logout_response(self, session_id):
        self.send(LogoutResponse(
            host = self.sessions[session_id][host],
            port = self.sessions[session_id][port]
        ))
    def user_exited(self, dest_list, session_id ):
        for aSession in dest_list:
            m = UserExited(
                host = self.sessions[aSession][host],
                port = self.sessions[aSession][host],
                session_id  = session_id
            )
            self.send(m)
        






