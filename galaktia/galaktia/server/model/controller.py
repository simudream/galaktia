#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
ABC for controllers and base controller dispatcher model.
"""

from abc import ABCMeta, abstractmethod

class Controller(object):
    """ Abstract Base Class for controllers """
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, message):
        """
        Handles a request message and yields reponse and notification
        messages.

        :return: iterable of ``Message`` instances
        """

class DispatcherController(Controller):
    """
    Main controller for server-client protocol that dispatches messages
    to controllers according to message type.
    """

    def __init__(self, routes=None):
        """
        ``DispatcherController`` constructor.

        :parameters:
            routes : dict
                Maps message names to controllers that handle them.
        """
        self.routes = routes or {}

    def handle(self, message):
        """ Returns responses for given input message """
        controller = self.get_controller_for(message)
        if controller is not None:
            try:
                return controller.handle(message)
            except Exception: # if controller fails...
                logger.exception('Failed to handle message: %s', message)
        return [] # TODO: send "internal server error" message

    def get_controller_for(self, message):
        try:
            type = message.type
            return self.routes[type]
        except KeyError:
            logger.exception('Unknown message type: %s', message)
        except Exception:
            logger.exception('Bad message: %s', message)
        return None

