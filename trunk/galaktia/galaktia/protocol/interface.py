#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, logging

from pyglet.event import EventDispatcher

from galaktia.protocol.base import BaseServer, BaseClient
from galaktia.protocol.codec import ProtocolCodec
from galaktia.protocol.controller import Controller
from galaktia.protocol.operations.join import *
from galaktia.protocol.operations.talk import *
from galaktia.protocol.operations.move import *
from galaktia.protocol.operations.exit import *


logger = logging.getLogger(__name__)


class GalaktiaClientController(EventDispatcher, Controller):
    def greet(self):
        self.dispatch_event('on_greet')
        return []

    def __PlayerEnteredLOS(input_message):
        session_id = input_message['subject']
        (x,y) = input_message['object']
        description = input_message['description']
        self.dispatch_event('on_player_entered_los',
                 session_id, (x,y), description )
                 
    def __PlayerMoved(input_message):
        other_session_id = input_message["subject"]
        (dx, dy) = input_message["action"]
        (x,y) = input_message["object"]
        self.dispatch_event('on_player_moved',
                 other_session_id, (dx,dy), (x,y))
                 

    def __SayThis(input_message):
        message = input_message['action']
        self.dispatch_event('on_say_this', message)

    def __SomeoneSaid(input_message):
        message = input_message['action']
        username = input_message['subject']
        self.dispatch_event('on_someone_said', username, message)
        
    def __UserAccepted(input_message):
        if input_message['accepted']:
            username = input_message['username']
            x, y = input_message['player_initial_state']
            surroundings = input_message['surroundings']
            self.dispatch_event('on_user_accepted', username, (x,y), surroundings)
        else:
            self.dispatch_event('on_user_rejected')
     # Join commands
     
    def __CheckProtocolVersion(input_message):
        version = input_message['version']
        url = input_message['url']
        session_id = input_message.session.id
        self.dispatch_event('on_check_protocol_version', session_id, version, url)
        
    def __UserJoined(input_message):
        username = input_message['username']
        self.dispatch_event('on_user_joined', username)
        
    # Exit Commands
    def __LogoutResponse(input_message):
        self.dispatch_event('on_logout_response')
        
    def __UserExited(input_message):
        session_id = input_message['subject']
        username = input_message['object']
        self.dispatch_event('on_user_exited', session_id, username)
    
    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')

        if command == None:
            return []

        #Talk commands
        
        command_handler = {
        u'PlayerEnteredLOS': self.__PlayerEnteredLOS,
        u'PlayerMoved': self.__PlayerMoved,
        u'SomeoneSaid': self.__SomeoneSaid,
        u'UserAccepted': self.__UserAccepted,
        u'CheckProtocolVersion': self.__CheckProtocolVersion,
        u'UserJoined': self.__UserJoined,
        u'SayThis': self.__SayThis,
        u'LogoutResponse': self.__LogoutResponse}
        try:
            command_handler[command](input_message)
        except KeyError:
            raise ValueError, "Invalid command: %s" % command
        return []



GalaktiaClientController.register_event_type('on_greet')
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
    def __init__(self, session_dao, (host, port)):
        BaseClient.__init__(self, ProtocolCodec(session_dao),
                             GalaktiaClientController(), host, port)
        
        self.controller.push_handlers(self)
        
        self.session_dao = session_dao
    
    # Event Handlers
    def on_greet(self):
        raise NotImplementedError
    def on_player_moved(self, other_session_id, (dx,dy), (x,y)):
        raise NotImplementedError
    def on_player_entered_los(self, session_id, (x,y), description):
        raise NotImplementedError
    def on_someone_said(self, username, message):
        raise NotImplementedError
    def on_check_protocol_version(self, session_id, version, url):
        raise NotImplementedError
    def on_user_accepted(self, username, (x, y), surroundings):
        raise NotImplementedError
    def on_user_rejected(self):
        raise NotImplementedError
    def on_user_joined(self, username):
        raise NotImplementedError
    def on_logout_response(self):
        raise NotImplementedError
    def on_user_exited(self, session_id, username):
        raise NotImplementedError
    
    
    # Convinience protocol methods
    def move_dx_dy(self,(dx,dy)):
        m = MoveDxDy(session=self.session, delta=(dx, dy))
        self.send(m)
        
    def say_this(self,message):
        m = SayThis(message=message, session=self.session)
        self.send(m)
        
    def request_user_join(self,username):
        self.send(RequestUserJoin(username = username, session=self.session))
        
    def start_connection(self):
        logger.info('Starting connection...')
        self.send(StartConnection(session=self.session))
        
    def logout_request(self):
        self.send(LogoutRequest(session=self.session))

class GalaktiaServerController(EventDispatcher, Controller):
    """ Implementation of a simple chat server """

    def process(self, input_message):
        """ Implements processing by returning CamelCased input 
            Please see protocol specification for more on messages
        """
        command = input_message.get('name')

        def __MoveDxDy(input_message):
            (dx, dy) = input_message['action']
            self.dispatch_event('on_move_dx_dy', input_message.session, (dx,dy))

        def __SayThis(input_message):
            message = input_message['action']
            self.dispatch_event('on_say_this', input_message.session, message)

        def __RequestUserJoin(input_message):
            username = input_message['username']
            self.dispatch_event('on_request_user_join', input_message.session, username)
        def __StartConnection(input_message):
            self.dispatch_event('on_start_connection', input_message.session)
        def __LogoutRequest(input_message):
            self.dispatch_event('on_logout_request', input_message.session)
        function_handlers = {
            u'MoveDxDy': __MoveDxDy,
            u'SayThis': __SayThis,
            u'RequestUserJoin': __RequestUserJoin,
            u'StartConnection': __StartConnection,
            u'LogoutRequest': __LogoutRequest}
        try:
            function_handlers[command](input_message)
        except KeyError:
            raise ValueError("Invalid command: %s" % command)

        #should return [input_message.acknowledge()]
        return []

GalaktiaServerController.register_event_type('on_move_dx_dy')
GalaktiaServerController.register_event_type('on_say_this')
GalaktiaServerController.register_event_type('on_request_user_join')
GalaktiaServerController.register_event_type('on_start_connection')
GalaktiaServerController.register_event_type('on_logout_request')


class ServerProtocolInterface(BaseServer):
    """ Convenience server interface """

    #Overrides
    def __init__(self, session_dao):
        BaseServer.__init__(self, ProtocolCodec(session_dao), 
                            GalaktiaServerController())
        self.controller.push_handlers(self)

    # Event Handlers
    # To be implemented by class user

    def on_move_dx_dy(self, session, (dx,dy)):
        raise NotImplementedError
    def on_say_this(self, session, message):
        raise NotImplementedError
    def on_request_user_join(self, username):
        raise NotImplementedError
    def on_start_connection(self, session ):
        raise NotImplementedError
    def on_logout_request(self, session):
        raise NotImplementedError


    # Convinience protocol methods
    def player_entered_los(self, session_list, session, position, description):
        for aSession in session_list:
            m = PlayerEnteredLOS(session_id = session.id,
                position = position,
                description = description,
                session = aSession
                )
            self.send(m)

    def player_moved(self, session_list, mover_session, (dx,dy), (x,y)):
        for aSession in session_list:
            m = PlayerMoved(session_id = mover_session.id,delta = (dx,dy),
                position = (x,y),
                session = aSession
                )
            self.send(m)

    def someone_said(self, session_list, username, message):
        for aSession in session_list:
            self.send(SomeoneSaid(
                username = username,
                message = message, 
                session = aSession
                ))

    def user_accepted(self, session, username, player_initial_state, surroundings):
        self.send(UserAccepted( accepted = True, 
                            session_id = session.id,
                            username = username,
                            player_initial_state = player_initial_state,
                            session = session,
                            surroundings = surroundings
                            ))

    def user_rejected(self, session):
        self.send(UserAccepted(session=session, accepted=False))

    def check_protocol_version(self, session, version, url):
        self.send(CheckProtocolVersion(session=session, version=version, url=url))

    def user_joined(self, session_list, username):
        for aSession in session_list:
            self.send(UserJoined( username = username,
                session = aSession
                ))

    def logout_response(self, session):
        self.send(LogoutResponse(
            session = session
        ))

    def user_exited(self, session_list, session, username ):
        for aSession in session_list:
            self.send( UserExited(
                session_id = session.id,
                username  = username,
                session = aSession
            ) )

