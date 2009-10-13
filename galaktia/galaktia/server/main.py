#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging, os.path
from random import randint

from twisted.internet import reactor
from twisted.python import log

from galaktia.protocol.interface import ServerProtocolInterface
from galaktia.protocol.model import SessionDAO, Session
from galaktia.server.persistence.dao import WallDAO, CharacterDAO, \
        UserDAO, mass_unpack
from galaktia.server.persistence.orm import Wall, Character, \
        init_db, User
from galaktia.protocol.key import KeyGenerator


#logger = logging.getLogger(__name__)

SERVER_VERSION = "0.2"


class CamelCaseChatServer(ServerProtocolInterface):
    """ Implementation of a simple chat server :"""

    def __init__(self, session):
        self.session=session
            # Database session. Please, do not touch :P
        
        self.user_dao = UserDAO(session())
        self.char_dao = CharacterDAO(session())
        self.wall_dao = WallDAO(session())
        self.session_dao = SessionDAO()
            
        ServerProtocolInterface.__init__(self, self.session_dao)    

    def on_say_this(self, session, message):
        self.someone_said(
                session_list = self.session_dao.get_logged(),
                username = session.user.name,
                message = message
                )

    def on_request_user_join(self, session, username):
            user = self.user_dao.get_by(name=username)
            if not user:
                user = User(name=username, passwd= u'', email=username)
                # Set mail to username so as to avoid the unique constraint
                self.user_dao.add(user)
                self.user_dao.session.flush()
            elif self.session_dao.get_by(user_id=user.id):
                self.user_rejected(session=session)
                return
            session.user = user
            self.session_dao.set(session)
            self.user_joined(username=username, session_list=self.session_dao.get_logged())

            if not user.character:
                character = Character()
                character.name = username
                character.x, character.y = (randint(1,19),randint(1,19))
                character.z = 0
                character.level = 42 # I see dead people (?)
                character.user_id = user.id
                # character.collide = True

                self.char_dao.add(character)
                self.char_dao.session.flush()
                    # This should be done by another thread, watching the
                    # changes and commiting them.

                user.character = character
            else:
                character = user.character
                # Make sure the user is shown correctly
                # character.show = True
            self.char_dao.materialize(user.character, collide=True)

            layer = self.wall_dao.all()
            wall_list = mass_unpack(layer)

            self.user_accepted( 
                    session = session,
                    player_initial_state = (user.character.x, character.y),
                    username = user.name,
                    surroundings = wall_list
                    )
            session.user_id = user.id
            session.user = user
            session.secret_key = KeyGenerator.generate_key(session.id, (username))

            # Let players know that a new dude is in town
            self.player_entered_los(self.session_dao.get_logged(), session,
                    (character.x, character.y), username)
                # Use self.char_dao.get_near(character, radius=10) instead of
                # get_logged()

            # for aSession in filter(lambda x: x != session_id, self.sessions):
            for aSession in [ sth for sth in self.session_dao.get_logged() if sth.user.character in \
                                    self.char_dao.get_near(character,
                                    radius=20) and sth.user.character.show]:
                # Explicación: pide todas las sessions (no propias), pero
                # que además tengan un personaje asociado y que estén
                # dentro de radio 20 del usuario. Es más, el if x != no es
                # necesario.
                pos = (aSession.user.character.x, \
                    aSession.user.character.y)
                self.player_entered_los([session], aSession, pos, aSession.user.character.name)


    def on_start_connection(self, session):
        self.check_protocol_version(session, 
                                    version = SERVER_VERSION, 
                                    url="http://www.galaktia.com.ar")

    def on_logout_request(self, session):
        print "on logout request!"
        if session is not None:
            username = session.user.name
            self.logout_response(session)
            self.char_dao.dismiss(session.user.character)
            self.user_exited(self.session_dao.get_logged(), session, username)
            self.session_dao.delete(session)

    def on_move_dx_dy(self, session, (dx,dy)):
        character = session.user.character
        newx, newy = (character.x+dx, character.y+dy)

        if self.char_dao.move(character, newx, newy):
            self.player_moved(self.session_dao.get_logged(), session, (dx, dy), (newx, newy))
        elif dx * dy != 0:
            if self.char_dao.move(character, newx-dx, newy):
                self.player_moved(self.session_dao.get_logged(), session, (0, dy), (newx-dx, newy))
            elif self.char_dao.move(character, newx, newy-dy):
                self.player_moved(self.session_dao.get_logged(), session, (dx, 0), (newx, newy-dy))
        # TODO: This should be handled entirely by the new Positional engine.


def get_session():
    here_dir = os.path.dirname(__file__)
    path = os.path.join(here_dir, '..', 'server', 'data', 'map.sqlite3')
    db_conn_str = 'sqlite:///%s' % path
    #logger.info('Using database connection string: %s', db_conn_str)
    engine, metadata, session = init_db(db_conn_str)
    return session

def main(program, port=6414):
    """ Main program: Starts a server on given port """
    # log.startLogging(sys.stderr) # enables Twisted logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    protocol = CamelCaseChatServer(get_session())
    #logger.info("Starting %s", "server")
    port = int(port)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__':
    print 'Usage: python -m galaktia.server.main [port]'
    main(*sys.argv)

