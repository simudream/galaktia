#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Controllers Abstract Base Classes
"""

import logging

from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)

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

class BaseDispatcherController(Controller):
    """ Abstract Base Class for a front controller that dispatches messages
        to particular controllers in order to handle them """
    __metaclass__ = ABCMeta

    def handle(self, message):
        """ Dispatches input message to corresponding controller
            in order to handle it and return its output messages """
        try:
            controller = self.get_controller_for(message)
        except Exception:
            logger.exception('No controller found to dispatch message: %s', \
                    message)
            return []
        try:
            return controller.handle(message)
        except Exception:
            logger.exception('Failed to handle message: %s', message)
            return []

    @abstractmethod
    def get_controller_for(self, message):
        """ :return: controller that handles given message """

