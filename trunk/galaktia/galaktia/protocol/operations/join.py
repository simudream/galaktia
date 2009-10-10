#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.protocol.model import Message


"""
***********************************************************************
                               Join
***********************************************************************
Client:                                                     Server:
            StartConection      - >

                                < -  CheckProtocolVersion

            RequestUserJoin     - >

                                < -  UserAccepted

                                < -  UserJoined[All]

            UserAcceptedAck     - >

"""

class StartConnection(Message):
    """ C->S Message for informing the server that a client wants to start a
    connection with him and so proceed with handshaking."""
    def __init__(self, **kargs):
        super(StartConnection, self).__init__(**kargs)

class CheckProtocolVersion(Message):
    """ S->C Message for informing client current server protocol"""
    def __init__(self, **kwargs):
        super(CheckProtocolVersion, self).__init__(**kwargs)

class RequestUserJoin(Message):
    """ C->S Message for informing that a character with a certain username
    wants to enter Galaktia world. I'm Going in Boy!"""
    def __init__(self, username, **kwargs):
        super(RequestUserJoin, self).__init__(username= username, **kwargs)

class UserAccepted(Message):
    """ S->C Message for informing that a certain user was accepted or 
        rejected by server. If accepted, command also carries information
        about the session identifier and the player's initial state. """
    def __init__(self, accepted, surroundings=None, username=None, session_id=None, \
            player_initial_state=None, ack=None, **kwargs):
        kwargs.update({'accepted': accepted })


        if username is not None:
            kwargs['username'] = username

        if session_id is not None:
            kwargs['session_id'] = session_id

        if player_initial_state is not None:
            kwargs['player_initial_state'] = player_initial_state

        if surroundings is not None:
            kwargs['surroundings'] = surroundings

        super(UserAccepted, self).__init__(**kwargs)

class UserJoined(Message):
    """ S->C Message for informing all clients that a new client logged in"""
    def __init__(self, username, **kwargs):
        super(UserJoined, self).__init__({'username': username}, **kwargs)


