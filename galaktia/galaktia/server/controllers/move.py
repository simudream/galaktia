#!/usr/bin/python
# -*- coding: utf-8 -*-


from galaktia.protocol.controller import MessageController

from galaktia.protocol.operations.move import *

class MoveDxDyController(MessageController):
    
    MESSAGE_KEYS = ['action', 'timestamp']
    
    def __init__(self, session_dao, dao_resolver, engine_resolver):
        MessageController.__init__(self, session_dao, dao_resolver)
        
        self.char_dao = self.dao_resolver.char
        self.pos_engine = engine_resolver.positional
        
    def _process(self, session, (dx, dy), timestamp):
        character = self.char_dao.get_by(id=session.character_id)
        pos = self.pos_engine.d_move(character, (dx, dy))
        print pos
        if pos:
            for aSession in self.session_dao.get_logged():
                m = PlayerMoved(session_id=session.id,
                    delta=pos,
                    position=(character.x, character.y),
                    session=aSession)
                    # pos may be != (dx, dy). PS: pos = (newdx, newdy)
                yield m
