#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.server.model.controller import Controller
from galaktia.server.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class ExitRequestMessage(RequestMessage):
    pass

class ExitResponseMessage(ResponseMessage):
    pass

class ExitNotificationMessage(NotificationMessage):
    character_id = None

class ExitController(Controller):
    """ Handles "exit" events """

    dao = None # galaktia.server.persistence.dao.DAOLocator

    def handle(self, message):
        # yield ExitResponseMessage(...)
        # yield ExitNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

