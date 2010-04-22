#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.model.controller import Controller
from galaktia.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class SayRequestMessage(RequestMessage):
    text = ''

class SayResponseMessage(ResponseMessage):
    pass

class SayNotificationMessage(NotificationMessage):
    character_id = None

class SayController(Controller):
    """ Handles "say" events """

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        response = SayResponseMessage()
        response._src_session = 1
        response._dst_session = 1
        if message.text:
            response.text = 'This is what you said reversed: ' + \
                    ''.join(reversed(message.text))
        else:
            response.text = 'You said nothing!'
        yield response
        # yield SayResponseMessage(...)
        # yield SayNotificationMessage(...)

