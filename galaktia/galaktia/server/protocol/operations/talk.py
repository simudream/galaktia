#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.server.protocol.operations.action import ActionRequest,
                        ActionResponse


class SayThis(ActionRequest):
    """ C->S Command for p2p chatting"""
    def __init__(self, **kwargs):
        kwargs['action'] = kwargs['message']

        # we use get below because if there's no-one to whisper to,
        # None will be sent in "object", and server will broadcast message
        kwargs['object'] = kwargs.get('whisper_to')
        ActionRequest.__init__(self, **kwargs)

class SayThisAck(Acknowledge):
    """ S->C Acknowledge for SayThis Action"""
    pass

class SomeoneSaid(ActionUpdate):
    """ S->C Command for informing client that other client said something
        in chat. """
    def __init__(self, **kwargs):
        kwargs['username'] = kwargs['username']
        kwargs['action'] = kwargs['message']
        ActionResponse.__init__(self, **kwargs)

class SomeoneSaidAck(Acknowledge):
    """ S->C Acknowledge for SomeoneSaid Action"""
    pass


