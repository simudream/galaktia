#!/usr/bin/python
# -*- coding: utf-8 -*-


from galaktia.protocol.controller import MessageController

from galaktia.protocol.operations.move import *

class MoveDxDyController(MessageController):
    
    MESSAGE_KEYS = ['action', 'timestamp']
    
    def __init__(self, session_dao, dao_resolver, pos_engine):
        MessageController.__init__(self, session_dao, dao_resolver)
        
        self.pos_engine = pos_engine
        
    def _process(self, session, (dx, dy), timestamp):
        character = session.user.character
        pos = self.pos_engine.d_move(character, (dx, dy))
        if pos:
            for aSession in self.session_dao.get_logged():
                m = PlayerMoved(session_id = session.id,
                    delta = (dx, dy),
                    position = (character.x, character.y),
                    session = aSession
                    )
                yield m
#       if timestamp * 1000 - character.last_move_timestamp < 200:
#           return
#       character.last_move_timestamp = timestamp * 1000
#       newx, newy = (character.x+dx, character.y+dy)
#
#       if self.char_dao.move(character, newx, newy):
#           self.player_moved(self.session_dao.get_logged(), session, (dx, dy), (newx, newy))
#       elif dx * dy != 0:
#           if self.char_dao.move(character, newx-dx, newy):
#               self.player_moved(self.session_dao.get_logged(), session, (0, dy), (newx-dx, newy))
#           elif self.char_dao.move(character, newx, newy-dy):
#               self.player_moved(self.session_dao.get_logged(), session, (dx, 0), (newx, newy-dy))
#       # TODO: This should be handled entirely by the new Positional engine.
