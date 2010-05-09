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
    text = ''
    character_id = None

class SayController(Controller):
    """ Handles "say" events """

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        response = SayResponseMessage()
        response._dst_session = message._src_session
        response.text = message.text # formerly: 'Batman' :)
        yield response # responds same text (echo service)

        if message.text:
            me = self.dao.character.get(message._src_session)
            others = self.dao.spatial.get_near(me, radius = 20)

            for other in others:
                notification = SayNotificationMessage()
                notification._dst_session = other.id
                notification.text = 'Batman'
                yield notification

        # yield SayResponseMessage(...)
        # yield SayNotificationMessage(...)

