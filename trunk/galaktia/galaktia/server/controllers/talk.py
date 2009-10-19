#!/usr/bin/python
# -*- coding: utf-8 -*-


from galaktia.protocol.controller import MessageController

from galaktia.protocol.operations.talk import *

class SayThisController(MessageController):
    
    MESSAGE_KEYS = ['action']
    
    def __init__(self, session_dao, dao_resolver):
        
        MessageController.__init__(self, session_dao, dao_resolver)
        
        self.char_dao = self.dao_resolver.char
        self.user_dao = self.dao_resolver.user
    
    def _process(self, session, action):
        
        character = self.char_dao.get_by(id=session.character_id)
        user = self.user_dao.get_by(id=character.user_id)
        username = user.name
        
        for aSession in self.session_dao.get_logged():
            m = SomeoneSaid(
                username=username,
                message=action, 
                session=aSession
                )
            yield m