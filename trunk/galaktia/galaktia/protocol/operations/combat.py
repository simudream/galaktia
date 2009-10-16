#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.protocol.operations.action import ActionRequest, \
                        ActionResponse, ActionUpdate

"""
***********************************************************************
                               Combat
***********************************************************************
Client:                                                     Server:
            AttackRequest       - >

                                < -  AttackUpdate[Some]

                                < -  ObjectWasHit[Some]

                                < -  ObjectDestroyed[Some]

                                < -  CharacterResurrected[Some]

"""

class AttackRequest(ActionRequest):
    """ C->S Command for hitting other character"""
    def __init__(self, **kwargs):
        # para pensar (?): está bien que el cliente le pase la weapon?
        # o el server debería "poner" esa info?
        kwargs['action'] = kwargs.get('weapon') # The object with which to attack.
        kwargs['object'] = kwargs['target'] # The object which is attacked.
        ActionRequest.__init__(self, **kwargs)

class AttackUpdate(ActionUpdate):
    """ S->C Command to tell the client that a character attempts an attack"""
    def __init__(self, **kwargs):
        kwargs['subject'] = None
        kwargs['action'] = kwargs.get('damage') # If applicable, informs damage
                                                # made. Only to use when player's 
                                                # character is hit.

        kwargs['object'] = kwargs['incordiado'] # Object that was attacked.
        ActionUpdate.__init__(self, **kwargs)

class ObjectWasHit(ActionUpdate):
    """ S->C Command to tell the client that an object
     was attacked successfully"""
    def __init__(self, **kwargs):
        kwargs['subject'] = None
        kwargs['action'] = kwargs.get('damage') # If applicable, informs damage
                                                # made. Only to use when player's 
                                                # character is hit.

        kwargs['object'] = kwargs['incordiado'] # Object that was attacked.
        ActionUpdate.__init__(self, **kwargs)

class ObjectDestroyed(ActionUpdate):
    """S->C command to tell the client that an object was obliterated"""
    def __init__(self, **kwargs):
        kwargs['subject'] = None
        kwargs['action'] = kwargs.get('drama_level') # Extensible for critical
                                                     # hits and that things.
        kwargs['object'] = kwargs['destroyed'] # Object that was obliterated
        ActionUpdate.__init__(self, **kwargs)

class CharacterResurrected(ActionUpdate):
    """S->C command to tell de client that a character/monster was revived"""
    def __init__(self, **kwargs):
        kwargs['subject'] = None
        kwargs['action'] = None
        kwargs['object'] = kwargs['resurrectee'] # lazarus come forth
                                                 #           [Jn 11:1-45]
        ActionUpdate.__init__(self, **kwargs)

