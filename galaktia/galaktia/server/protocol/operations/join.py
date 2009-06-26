#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.server.protocol.model import Command


class StartConection(Command):
    """ C->S Command for informing the server that a client wants to start a
    connection with him and so proceed with handshaking."""
    pass

class CheckProtocolVersion(Command):
    """ S->C Command for informing client current server protocol"""
    def __init__(self, **kwargs):
        self['version'] = kwargs.get('version')
        self['url'] = kwargs.get('url')
        Command.__init__(self, **kwargs)

class RequestUserJoin(Command):
    """ C->S Command for informing that a character with a certain username
    wants to enter Galaktia world. I'm Going in Boy!"""
    def __init__(self, **kwargs):
        self['username'] = kwargs.get('username')
        Command.__init__(self, **kwargs)

class UserAccepted(Command):
    """ S->C Command for informing that a certain user  was accepted or 
        rejected by server"""
    def __init__(self, **kwargs):
        self['accepted'] = kwargs.get('accpeted')
        if self['accepted'] is True:
            self["session_id"] = kwargs.get('session_id')
            self["session_id"] = kwargs.get('session_id')

        Command.__init__(self, **kwargs)

class UserJoined(Command):
    """ S->C Command for informing all clients that a new client logged in"""
    pass

class UserAcceptedAck(Command):
    """ C->S Command for acknowledgeing UserAccepted when accepted"""
    pass
