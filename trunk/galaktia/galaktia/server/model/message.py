#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Messages are DTOs to be sent from client to server and viceversa
holding necessary information for each event request, response
and notification. This information is to be used by controllers
on each endpoint to apply changes to the game state.
"""

from abc import ABCMeta, abstractmethod

class Message(object):
    """ Base message class """
    __metaclass__ = ABCMeta

    _src_session = None
    _dst_session = None

class RequestMessage(Message):
    """ Base request message class (from client to server) """

class ResponseMessage(Message):
    """ Base response message class (from server to same client) """

class NotificationMessage(Message):
    """ Base notification message class (from server to another client) """

# Q: Why this useless class hierarchy?
# A: I don't know

