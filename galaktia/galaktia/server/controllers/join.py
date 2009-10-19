#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from time import time

from galaktia.protocol.model import Session
from galaktia.protocol.key import KeyGenerator
from galaktia.protocol.controller import MessageController
from galaktia.protocol.operations.join import *
from galaktia.protocol.operations.move import PlayerEnteredLOS

from galaktia.server.persistence.dao import mass_unpack
from galaktia.server.persistence.orm import Wall, Character, \
        init_db, User

        
SERVER_VERSION='0.2'

class RequestUserJoinController(MessageController):
    
    MESSAGE_KEYS = ['username']
    
    def __init__(self, session_dao, dao_resolver):
        MessageController.__init__(self, session_dao, dao_resolver)
        
        self.user_dao = self.dao_resolver.user
        self.char_dao = self.dao_resolver.char
        self.wall_dao = self.dao_resolver.wall
    
    def _process(self, session, username):
        user = self.user_dao.get_by(name=username)
        if not user:
            user = User(name=username, passwd= u'', email=username)
            # Set mail to username so as to avoid the unique constraint
            self.user_dao.add(user)
            self.user_dao.session.flush()
        else:
            character = user.character
            if self.session_dao.get_by(character.id):            
                yield UserAccepted(session=session, accepted=False)
                return
        
        
        for aSession in self.session_dao.get_logged():
            yield UserJoined(username=username,
                             session=aSession)

        if not user.character:
            character = Character()
            character.name = username
            character.x, character.y = (randint(1,19),randint(1,19))
            character.z = 0
            character.arrival_timestamp = time()
            character.speed = 7
            character.level = 42 # I see dead people (?)
            character.user_id = user.id
            character.last_move_timestamp = 0
            character.life = 10 # for simplicity's sake
            # character.collide = True

            self.char_dao.add(character)
            self.char_dao.session.flush()
                # This should be done by another thread, watching the
                # changes and commiting them.

            user.character = character
        else:
            character = user.character
            character.speed = 7
            # Make sure the user is shown correctly
            # character.show = True
        self.char_dao.materialize(user.character, collide=True)

        layer = self.wall_dao.all()
        wall_list = mass_unpack(layer)

        yield UserAccepted(accepted=True,
                           surroundings=wall_list,
                           username=user.name,
                           session_id=session.id,
                           player_initial_state={
                               'starting_pos':(user.character.x, character.y),
                               'hps' : user.character.life
                           },
                           session=session)
        
        # Regenerate the session with newly obtained data
        key = KeyGenerator.generate_key(session.id, (username))
        session = Session(id=session.id, 
                          host=session.host, 
                          port=session.port, 
                          character_id=character.id, 
                          secret_key=key)
        self.session_dao.set(session)

        # Let players know that a new dude is in town
            # Use self.char_dao.get_near(character, radius=10) instead of
            # get_logged()
            
#        for aSession in self.session_dao.get_logged():
        for char in self.char_dao.get_los(character, 10):
            
            aSession = self.session_dao.get_by(char.id)
            yield PlayerEnteredLOS(session_id = session.id,
                position = (character.x, character.y),
                description = username,
                session = aSession
                )
            
        for character in self.char_dao.get_los(character, radius=10, return_self=True):
            
            char_session = self.session_dao.get_by(character.id)
            user = self.user_dao.get_by(id=character.user_id)
            
            pos = (character.x, character.y)
            yield PlayerEnteredLOS(session=session, 
                                   session_id=char_session.id, 
                                   position=pos, 
                                   description=user.name)
    
class StartConnectionController(MessageController):
    
    def _process(self, session):
        yield CheckProtocolVersion(session=session, 
                                   version = SERVER_VERSION, 
                                   url="http://www.galaktia.com.ar")
    