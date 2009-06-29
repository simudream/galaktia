#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.server.protocol.operations.action import ActionRequest, \
                        ActionResponse, ActionUpdate
from galaktia.server.protocol.model import Acknowledge


class MoveDxDy(ActionRequest):
    """ C->S Command for moving a character"""
    def __init__(self, **kwargs):
        kwargs['action'] = kwargs['delta']
        kwargs['object'] = None
        ActionRequest.__init__(self, **kwargs)

class PlayerEnteredLOS(ActionUpdate):

    def __init__(self, **kwargs):
        kwargs['action'] = None
        kwargs['object'] = kwargs['position']
        ActionRequest.__init__(self, **kwargs)

class PlayerMoved(ActionUpdate):

    def __init__(self, **kwargs):
        kwargs['action'] = None
        kwargs['object'] = kwargs['position']
        ActionRequest.__init__(self, **kwargs)

class PlayerSeenAck(Acknowledge):
    """ C->S Acknowledge for PlayerEnteredLOS Action"""
    pass


