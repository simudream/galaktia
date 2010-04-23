#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

from galaktia.model.mapdata import MapData
from galaktia.model.controller import Controller
from galaktia.model.message import RequestMessage, ResponseMessage, \
    NotificationMessage

logger = logging.getLogger(__name__)

class EnterRequestMessage(RequestMessage):
    username = None
    password = None

class EnterResponseMessage(ResponseMessage):
    x = None
    y = None
    character = None
    dyn_data = [] #
    sta_data = []
    map_data = [] # iterable with newly seen objects (dynamic and static)

class EnterNotificationMessage(NotificationMessage):
    x = None
    y = None
    character = None

class EnterController(Controller):
    """ Handles "enter" events """

    dao = None # galaktia.persistence.dao.DAOLocator

    def handle(self, message):
        # yield EnterResponseMessage(...)
        # yield EnterNotificationMessage(...)
        user = self.dao.user.get_login_info(message.username, message.password) # magic
        if not user:
            user = self.dao.user.new()
            char = Character()
        
        erm = EnterResponseMessage()
        char = self.dao.character.get_by_user_id(user.id)[0]
        sta_data = self.dao.wall.get_near(erm.character, radius=20)
        map_data = self.dao.ground.get_near(erm.character, radius=20)
        dyn_data = self.dao.character.get_near(erm.character, radius=20)
        erm.character, erm.sta_data = char, sta_data
        erm.map_data, erm.dyn_data = map_data, dyn_data
        erm._dst_session = char.id
        yield erm
        for i in erm.dyn_data:                
            enm = EnterResponseMessage()
            enm._dst_session = i.id
            enm.x, enm.y = char.pos[0:2]
            enm.character = char
            yield enm
            
        # raise NotImplementedError('Not yet implemented')

