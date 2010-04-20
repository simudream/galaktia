#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.model.controller import Controller
from galaktia.model.message import RequestMessage, ResponseMessage, \
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

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        # yield ExitResponseMessage(...)
        # yield ExitNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

