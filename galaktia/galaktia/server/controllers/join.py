#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from time import time

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
        elif self.session_dao.get_by(user_id=user.id):
            
            yield UserAccepted(session=session, accepted=False)
            return
        session.user = user
        self.session_dao.set(session)
        
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
            character.life = 100 # for simplicity's sake
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
        session.character_id = character.id
        session.user = user
        session.secret_key = KeyGenerator.generate_key(session.id, (username))

        # Let players know that a new dude is in town
            # Use self.char_dao.get_near(character, radius=10) instead of
            # get_logged()
            
        for aSession in self.session_dao.get_logged():
            yield PlayerEnteredLOS(session_id = session.id,
                position = (character.x, character.y),
                description = username,
                session = aSession
                )
        
        for aSession in [ sth for sth in self.session_dao.get_logged() if sth.user and sth.user.character in \
                                self.char_dao.get_near(character,
                                radius=20) and sth.user.character.show]:
            # Explicación: pide todas las sessions (no propias), pero
            # que además tengan un personaje asociado y que estén
            # dentro de radio 20 del usuario. Es más, el if x != no es
            # necesario.
            pos = (aSession.user.character.x, \
                aSession.user.character.y)
            yield PlayerEnteredLOS(session=session, 
                                   session_id=aSession.id, 
                                   position=pos, 
                                   description=aSession.user.character.name)
    
class StartConnectionController(MessageController):
    
    def _process(self, session):
        yield CheckProtocolVersion(session=session, 
                                   version = SERVER_VERSION, 
                                   url="http://www.galaktia.com.ar")
    