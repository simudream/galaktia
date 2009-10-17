#!/usr/bin/python
# -*- coding: utf-8 -*-


from galaktia.protocol.controller import MessageController

from galaktia.protocol.operations.talk import *

class SayThisController(MessageController):
    
    MESSAGE_KEYS = ['action']
    
    def _process(self, session, action):
        
        for aSession in self.session_dao.get_logged():
            m = SomeoneSaid(
                username = session.user.name,
                message = action, 
                session = aSession
                )
            yield m