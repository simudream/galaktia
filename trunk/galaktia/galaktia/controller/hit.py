#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.model.controller import Controller
from galaktia.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class HitRequestMessage(RequestMessage):
    character_id = None

class HitResponseMessage(ResponseMessage):
    result = None

class HitNotificationMessage(NotificationMessage):
    hitting_character_id = None
    hit_character_id = None
    result = None

class HitController(Controller):
    """ Handles "hit" events """

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        # yield HitResponseMessage(...)
        # yield HitNotificationMessage(...)
        raise NotImplementedError('Not yet implemented')

