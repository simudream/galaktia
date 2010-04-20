#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.server.model.controller import Controller
from galaktia.server.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class EnterRequestMessage(RequestMessage):
    username = None
    password = None

class EnterResponseMessage(ResponseMessage):
    x = None
    y = None
    character = None
    map_data = [] # iterable with newly seen objects (dynamic and static)

class EnterNotificationMessage(NotificationMessage):
    x = None
    y = None
    character = None

class EnterController(Controller):
    """ Handles "enter" events """

    dao = None # galaktia.server.persistence.dao.DAOLocator

    def handle(self, message):
        # yield EnterResponseMessage(...)
        # yield EnterNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

