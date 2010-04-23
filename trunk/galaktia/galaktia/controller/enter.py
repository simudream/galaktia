#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging

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

        # fetch the user from the database
        user = self.dao.user.get_login_info(message.username, message.password) 

        # if there's no user, create it (we should send a noUserNotification)
        if not user:
            # create and add an user
            user = self.dao.user.new(username=message.username,
                passwd=message.password)
            self.dao.user.flush()

            # create and add a character
            self.dao.character.new(name=username, x=0, y=0, z=0)
            self.dao.character.flush()

        # create a response message
        erm = EnterResponseMessage()

        # fetch the character from the database
        char = self.dao.character.get_by_user_id(user.id)[0]
        sta_data = self.dao.wall.get_near(erm.character, radius=20)
        map_data = self.dao.ground.get_near(erm.character, radius=20)
        dyn_data = self.dao.character.get_los(erm.character, radius=20)
        erm.character, erm.sta_data = char, sta_data
        erm.map_data, erm.dyn_data = map_data, dyn_data
        erm._dst_session = char.id
        yield erm

        # Notify all users in LoS
        for i in erm.dyn_data:                
            enm = EnterResponseMessage()
            enm._dst_session = i.id
            enm.x, enm.y = char.pos[0:2]
            enm.character = char
            yield enm
