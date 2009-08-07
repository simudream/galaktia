#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class Datagram(object):
    """ Stores raw datagram bytes (str), host (str) and port (int) """

    def __init__(self, data, host=None, port=None):
        self.data, self.host, self.port = data, host, port

    def get_destination(self):
        destination = (self.host, self.port)
        return destination if None not in destination else None

class Message(dict):
    """ Represents a message to be sent or received via a protocol """

    def __init__(self, data=None, session=0):
        self.session = session
        
        self['name'] = self.__class__.__name__
        self['timestamp'] = time.time()
        self.update(data or {})

    # No need for Java-like getters and setters (especially in anti-
    # Pythonic camelCase) when we can access attrs directly:
    # def getHost(self): return self.host
    # def getPort(self): return self.port
    # def getSession(self): return self.session

    def acknowledge(self, data=None, **kwargs):
        ack_data = {'ack': self['timestamp']}
        ack_data.update(data or {})
        return Acknowledge(ack_data,
                           host = self.host, 
                           port = self.port, 
                           **kwargs)

class Command(Message):
    """ A client-server protocol command with an identifying name """
    # deprecated

class Acknowledge(Message):
    """ Message for acknowledgeing a command """

    def acknowledge(self, data, **kwargs):
        raise DeprecationWarning('Cannot acknowledge an Acknowledge message')

class Session(object):
    """ Represents a client-server session """

    def __init__(self, id=0):
        self.id = id
        # self.user = ...
        # self.player = ...

    def get_encryption_key(self):
        return self.id # TODO: should be a secret password

