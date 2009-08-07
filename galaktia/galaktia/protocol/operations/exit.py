#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.protocol.operations.action import ActionRequest, \
                        ActionResponse, ActionUpdate
from galaktia.protocol.base import Message


"""
***********************************************************************
                               Exit
***********************************************************************
Client:                                                     Server:
            StopPlayerSession    - >

                                < -  UserExited[All]

            UserExitedAck        - > 

- LogoutRequest: El cliente le envía al server un mensaje con su 
session_id dicéndole que quiere cerrar la sesión de ese personaje.

- UserExited: El server le envía un mensaje a todos los jugadores 
(incluído el que quiere irse) diciendo que el jugador se va del juego.
Incluye el identificador del jugador que se va. Al recibir este mensaje,
el cliente debe eliminarlo de su registro interno de jugadores en línea
de visión o hacer todos los cambios necesarios para eliminar completamente
el jugador del mundo virtual de galaktia.
"""

class LogoutRequest(ActionRequest):
    """ C->S Command for logging off a player account"""
    def __init__(self, **kwargs):
        kwargs['action'] = None
        kwargs['object'] = None
        ActionRequest.__init__(self, **kwargs)

class LogoutResponse(Message):
    """ S->C Command for allowing the user to disconnect"""
    def __init__(self, **kwargs):
        Message.__init__(self, **kwargs)

class UserExited(ActionUpdate):
    """ S->C Command for informing client that other client logged off. """
    def __init__(self, **kwargs):
        kwargs['subject'] = kwargs['session_id']
        kwargs['action'] = None
        kwargs['object'] = kwargs['username']
        ActionUpdate.__init__(self, **kwargs)





