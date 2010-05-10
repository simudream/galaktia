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
    engine = None # galaktia.engine.engine.EngineResolver

    def handle(self, message):
        
        me = self.dao.character.get(message._src_session)
        move_vector = (message.x, message.y)
        new_pos = self.engine.positional.d_move(me, move_vector)
        response = MoveResponseMessage()
        
        # shouldn't we respond that movement was invalid if new_pos is False?
        response.x, response.y = new_pos if new_pos else move_vector
        response.map_data = [] # TODO: should get newly seen objects from 
                               # database... dunno how yet
        yield response     
        
        if new_pos:
            others = self.dao.spatial.get_near(me, radius=20)

            for other in others:
                notification = MoveNotificationMessage()
                notification._dst_session = other.id
                notification.map_data = [(me.id, new_pos)]
                        # Should contain info about moved object.
                        # We should define an interface with client.
                        # Assuming arbitrarily (mover.id, (x,y))
                yield notification
    
