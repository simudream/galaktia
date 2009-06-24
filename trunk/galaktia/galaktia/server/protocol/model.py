#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Datagram(tuple):
    """ Stores raw datagram bytes (str), host (str) and port (str) """

class Message(dict):
    """ Represents a message to be sent or received via a protocol """

    def __init__(self, **kwargs):
        self['host'] = kwargs.get('host')
        self['port'] = kwargs.get('port')
        self.update(kwargs)

