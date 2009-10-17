#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log

from galaktia.protocol.base import BaseServer, BaseClient
from galaktia.protocol.codec import ProtocolCodec

#logger = logging.getLogger(__name__)

class Controller(object):

    def greet(self):
        """ Returns Message objects to be sent to start a connection """
        return [] # override in clients to start a connection

    def process(self, input_message):
        """ Returns an iterable of output messages in response to input """
        raise NotImplementedError

class MessageController(Controller):
    """ ``Controller`` adapter for processing messages """

    MESSAGE_KEYS = []

    def __init__(self, session_dao, dao_resolver):
        
        self.session_dao = session_dao
        self.dao_resolver = dao_resolver
        
        Controller.__init__(self)

    def process(self, input_message):
        return self._process(input_message.session, *self.get_args(input_message))

    def _process(self, session, *args):
        raise NotImplementedError('Abstract method')

    def get_args(self, input_message):
        return [input_message[key] for key in self.MESSAGE_KEYS]

class PlayerEnteredLOSController(MessageController):
    """ ``MessageController`` subclass example """

    MESSAGE_KEYS = ['subject', 'object', 'description']

    def _process(self, session, subject, object, description):
        raise NotImplementedError('TODO ;)') # TODO

class DispatcherController(Controller):
    """
    Main controller for server-client protocol that dispatches messages
    to controllers according to message name.
    """

    def __init__(self, routes=None):
        """
        ``DispatcherController`` constructor.

        :parameters:
            # TODO: all necessary DAOs, helpers, etc. to create controllers
        """
        self.routes = routes

    def process(self, input_message):
        """ Returns responses for given input message """
        try:
            command = input_message['name']
                    # raises KeyError if no name
        except Exception:
            logger.exception('Bad message: %s', input_message)
            return [] # TODO: maybe send back error message
        try:
            controller = self.routes[command]
                    # raises KeyError if command is unknown
        except Exception:
            logger.exception('Unknown message type: %s', input_message)
            return [] # TODO: maybe send back error message
        try:
            return controller.process(input_message)
                    # raises any Exception if controller fails
        except Exception:
            logger.exception('Failed to handle message: %s', input_message)
            return [] # TODO: send "internal server error" message