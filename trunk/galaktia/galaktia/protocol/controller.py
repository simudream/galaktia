#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Protocol controllers for processing received messages
"""

import logging

logger = logging.getLogger(__name__)

class Controller(object):
    """ Process incoming input from the protocol """

    def greet(self):
        """ Returns Message objects to be sent to start a connection """
        return [] # override in clients to start a connection

    def process(self, input_message):
        """
        Returns an iterable of output messages in response to input

        : parameters :
            input_message : Message
                The input to be processed
        """
        raise NotImplementedError

class MessageController(Controller):
    """ ``Controller`` adapter for processing messages """

    MESSAGE_KEYS = []

    def __init__(self, session_dao, dao_resolver):
        """
        Instance ``MessageController``

        : parameters :
            session_dao : SessionDAO
                The instance of ``SessionDAO`` to use when processing messages
            dao_resolver : DAOResolver
                ``DAOResolver`` instance
        """

        self.session_dao = session_dao
        self.dao_resolver = dao_resolver

        Controller.__init__(self)

    def process(self, input_message):
        """
        Process an incoming message

        Do *NOT* override this method unless necessary. See ``_process``.

        : parameters :
            input_message : Message
                A ``Message`` to process

        : return :
            ``Message`` to send as response
        """
        return self._process(input_message.session, \
                *self._get_args(input_message))

    def _process(self, session, *args):
        """
        Extensible method to process methods

        : paramaters :
            session : Session
                The session that sent the message.

        : return :
            list of ``Message`` in reply to the message
        """
        raise NotImplementedError('Abstract method')

    def _get_args(self, input_message):
        """
        Obtain the data from the message needed to process it.

        The name of the properties to strip is stored in ``MESSAGE_KEYS``

        : parameters :
            input_message : Message
                The ``Message`` to strip the data from.

        : return :
            list of parameters in the order specified in ``MESSAGE_KEYS``
        """
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
            routes : dict
                Maps ``Message`` names to ``MessageDispatcher`` sub-classes
                that handle them.
        """
        self.routes = routes or {}

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
