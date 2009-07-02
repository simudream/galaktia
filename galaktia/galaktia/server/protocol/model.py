#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class Datagram(object):
    """ Stores raw datagram bytes (str), host (str) and port (int) """

    def __init__(self, data, host=None, port=None):
        self.data, self.host, self.port = data, host, port

class Message(dict):
    """ Represents a message to be sent or received via a protocol """

    def __init__(self, host=None, port=None, session=0, **kwargs):
        self._host = host
        self._port = port
        self._session = session

        self['id'] = time.time()
        
        self.update(kwargs)
    
    def getPort(self):
        return self._port
    port = property(getPort)
    
    def getHost(self):
        return self._host
    host = property(getHost)
    
    def getSession(self):
        return self._session
    session = property(getSession)

class Command(Message):
    """ A client-server protocol command with an identifying name """

    def __init__(self, **kwargs):
        self['name'] = self.__class__.__name__
        Message.__init__(self, **kwargs)

class Acknowledge(Message):
    """ Message for acknowledgeing a command """

    def __init__(self, **kwargs):
        self['ack'] = kwargs.get('ack')
        self['id'] = time.time()
        Message.__init__(self, **kwargs)