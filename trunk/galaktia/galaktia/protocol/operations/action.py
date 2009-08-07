#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from galaktia.protocol.model import Message

"""
- Operaciones del protocolo relacionadas con las acciones del jugador:
Todas son de la forma "sujeto acción objeto" (ejemplo: un mensaje de
chat a alguien, un movimiento a un lugar, un ataque, una compra, una
adquisición, etc.):
* Sujeto: puede ser un identificador de jugador, ya sea int o str
* Acción: un código de operación con ciertos parámetros
* Objeto: coordenadas donde se encuentra el objeto afectado en el
mundo virtual (o quizás también su identificador, si las coordenadas
no interesan en la acción)

Genéricamente, se necesitan 4 tipos de mensaje para una acción:
1.  Action Request (del cliente al servidor, al solicitar realizar una acción)
1'. Action Response (del servidor al cliente, al autorizar la acción solicitada)
2.  Action Update (del servidor al cliente, al notificar la acción de
un tercero que afecta su entorno)
2'. Action Accept (del cliente al servidor, al confirmar que la acción
notificada fue recibida)

Idem anterior en cuanto a los acuses de recibo (ACK). Con eso estaría
cubierta la confiabilidad.

"""


class ActionMessage(Message):
    """ ?->? Generic command involved in the game actions protocol """

    def __init__(self, **kwargs):
        self['subject'] = kwargs['subject']
        self['action'] = kwargs['action']
        self['object'] = kwargs['object']
        Message.__init__(self, data=kwargs.get('data'), host=kwargs.get('host'), port=kwargs.get('port'), session=0)

class ActionRequest(ActionMessage):
    """ C->S Generic command that the client uses to inform the server that
        certain action wants to be taken. Waits for acknowledge"""

    def __init__(self, **kwargs):
        # Client to Server requests always carry session identifiers
        kwargs['subject'] = kwargs['session_id']
        ActionMessage.__init__(self, **kwargs)


class ActionResponse(Message):
    """ S->C Generic command that the server uses to inform the client about the
        outcome of certain action he requested to do. """

    pass

class ActionUpdate(ActionMessage):
    """ S->C Generic command that the server uses to inform the client about
        an action performed by other client or the game system"""

    pass

