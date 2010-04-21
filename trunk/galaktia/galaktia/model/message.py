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
    """ :ivar: Source session ID """
    _dst_session = None
    """ :ivar: Destination session ID """

    # NOTE: As far as there is one session per character,
    #       user character IDs can be used as session IDs

class RequestMessage(Message):
    """ Base request message class (from client to server) """

class ResponseMessage(Message):
    """ Base response message class (from server to same client) """

class NotificationMessage(Message):
    """ Base notification message class (from server to another client) """

class ErrorMessage(Message):
    """ Base error message class (form server to same client) """

