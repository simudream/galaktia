#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.server.protocol.operations.action import ActionRequest, \
                        ActionResponse, ActionUpdate
from galaktia.server.protocol.model import Acknowledge


"""
***********************************************************************
                               Talk
***********************************************************************
Client:                                                     Server:
            SayThis             - >

                                < -  SomeoneSaid[All]
"""

class SayThis(ActionRequest):
    """ C->S Command for p2p chatting"""
    def __init__(self, **kwargs):
        kwargs['action'] = kwargs['message']

        # we use get below because if there's no-one to whisper to,
        # None will be sent in "object", and server will broadcast message
        kwargs['object'] = kwargs.get('whisper_to')
        ActionRequest.__init__(self, **kwargs)


class SomeoneSaid(ActionUpdate):
    """ S->C Command for informing client that other client said something
        in chat. """
    def __init__(self, **kwargs):
        kwargs['subject'] = kwargs['username']
        kwargs['action'] = kwargs['message']
        kwargs['object'] = None
        ActionUpdate.__init__(self, **kwargs)

