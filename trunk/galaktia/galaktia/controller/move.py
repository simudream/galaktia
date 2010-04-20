#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.model.controller import Controller
from galaktia.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class MoveRequestMessage(RequestMessage):
    x = None
    y = None

class MoveResponseMessage(ResponseMessage):
    x = None
    y = None
    map_data = [] # iterable with newly seen objects (dynamic and static)

class MoveNotificationMessage(NotificationMessage):
    map_data = [] # iterable with moved object

class MoveController(Controller):
    """ Handles "move" events """

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        # yield MoveResponseMessage(...)
        # yield MoveNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

