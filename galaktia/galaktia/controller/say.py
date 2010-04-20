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
        # yield SayResponseMessage(...)
        # yield SayNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

