#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
import sys

from pyglet.event import EventDispatcher

from galaktia.protocol.base import BaseServer, BaseClient
from galaktia.protocol.controller import Controller
from galaktia.protocol.operations.join import *
from galaktia.protocol.operations.talk import *
from galaktia.protocol.operations.move import *
from galaktia.protocol.operations.exit import *
from galaktia.protocol.codec import ProtocolCodec

logger = logging.getLogger(__name__)


class GalaktiaClientController(EventDispatcher, Controller):



    def greet(self):
        self.dispatch_event('on_greet')
        return []

    # Move commands
    def __PlayerEnteredLOS(self, input_message):
        session_id = input_message['subject']
        (x,y) = input_message['object']
        description = input_message['description']
        self.dispatch_event('on_player_entered_los',
                 session_id, (x,y), description )

    def __PlayerMoved(self, input_message):
        other_session_id = input_message["subject"]
        (dx, dy) = input_message["action"]
        (x,y) = input_message["object"]
        self.dispatch_event('on_player_moved',
                 other_session_id, (dx,dy), (x,y))

    #Talk commands
    def __SayThis(self, input_message):
        message = input_message['action']
        self.dispatch_event('on_say_this', message)

    def __SomeoneSaid(self, input_message):
        message = input_message['action']
        username = input_message['subject']
        self.dispatch_event('on_someone_said', username, message)

    def __UserAccepted(self, input_message):
        if input_message['accepted']:
            username = input_message['username']
            x, y = input_message['player_initial_state']['starting_pos']
            hit_points = input_message['player_initial_state']['hps']
            surroundings = input_message['surroundings']
            self.dispatch_event('on_user_accepted', username, (x,y), \
                            hit_points, surroundings)
        else:
            self.dispatch_event('on_user_rejected')

    # Join commands
    def __CheckProtocolVersion(self, input_message):
        version = input_message['version']
        url = input_message['url']
        session_id = input_message.session.id
        self.dispatch_event('on_check_protocol_version', session_id, version, url)

    def __UserJoined(self, input_message):
        username = input_message['username']
        self.dispatch_event('on_user_joined', username)

    # Exit Commands
    def __LogoutResponse(self, input_message):
        self.dispatch_event('on_logout_response')

    def __UserExited(self, input_message):
        session_id = input_message['subject']
        username = input_message['object']
        self.dispatch_event('on_user_exited', session_id, username)

    command_handler = {
        u'PlayerEnteredLOS': __PlayerEnteredLOS,
        u'PlayerMoved': __PlayerMoved,
        u'SomeoneSaid': __SomeoneSaid,
        u'UserAccepted': __UserAccepted,
        u'CheckProtocolVersion': __CheckProtocolVersion,
        u'UserJoined': __UserJoined,
        u'SayThis': __SayThis,
        u'LogoutResponse': __LogoutResponse,
        u'UserExited': __UserExited}

    def process(self, input_message):
        """ Writes server response and prompts for a new message to send """
        command = input_message.get('name')

        if command == None:
            return []

        try:
            command_handler_function = \
                           GalaktiaClientController.command_handler[command]
        except KeyError:
            raise ValueError, "Invalid command @GalaktiaClientController: %s" % command
        command_handler_function(input_message)
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
    def on_player_moved(self, other_session_id, (dx, dy), (x, y)):
        raise NotImplementedError
    def on_player_entered_los(self, session_id, (x, y), description):
        raise NotImplementedError
    def on_someone_said(self, username, message):
        raise NotImplementedError
    def on_check_protocol_version(self, session_id, version, url):
        raise NotImplementedError
    def on_user_accepted(self, username, (x, y), hit_points, surroundings):
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

    def request_user_join(self, username, password):
        self.send(RequestUserJoin(username=username, password=password, session=self.session))

    def start_connection(self):
        logger.info('Starting connection...')
        self.send(StartConnection(session=self.session))

    def logout_request(self):
        self.send(LogoutRequest(session=self.session))



