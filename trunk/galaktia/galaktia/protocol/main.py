#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging, os.path
from random import randint

from twisted.internet import reactor
from twisted.python import log

from galaktia.protocol.interface import ServerProtocolInterface
from galaktia.server.persistence.dao import StationaryDAO, CharacterDAO, SessionDAO, UserDAO
from galaktia.server.persistence.orm import Stationary, Character, init_db, Session, User


logger = logging.getLogger(__name__)

SERVER_VERSION = "0.2"


class CamelCaseChatServer(ServerProtocolInterface):
    """ Implementation of a simple chat server """

    def __init__(self, session):
        self.session=session
            # Database session. Please, do not touch :P
        ServerProtocolInterface.__init__(self)
        
        self.user_dao = UserDAO(session)
        self.char_dao = CharacterDAO(session)
        self.stat_dao = StationaryDAO(session) # Useless ATM.
        self.session_dao = SessionDAO(session)
            

    def on_say_this(self, talking_user_id, message):
        self.someone_said(
                session_list = self.session_dao.all(),
                username = self.session_dao.get_by(id=talking_user_id).user.name,
                message = message
                )

    def on_request_user_join(self, host, port, username):
            user = self.user_dao.get_by(name=username)
            if not user:
                user = User(name=username, passwd='', email=username)
                # Set mail to username so as to avoid the unique constraint
                self.user_dao.add(user)
            
            session = self.session_dao.get_by(user_id=user.id)
            if not session:
                self.user_joined( username = username,
                            session_list = self.session_dao.all())
                
                session = Session(host=host, port=port, user_id=user.id)
                session.user = user
                
                if not user.character:
                    character = Character()
                    character.name = username
                    character.x, character.y = (randint(0,9),randint(0,9))
                    character.z = 0
                    character.level = 42 # I see dead people
                    character.user_id = user.id

                    self.char_dao.add(character)
                    self.char_dao.session.flush()
                        # This should be done by another thread, watching the
                        # changes and commiting them.

                    user.character = character
                else:
                    character = user.character
                    character.show = True

                # Make sure the user is shown correctly


                # for aSession in filter(lambda x: x != session_id, self.sessions):
                for aSession in [ sth for sth in self.session_dao.all() if sth.user.character in self.char_dao.get_near(character, radius=20)]:
                    # Explicación: pide todas las sessions (no propias), pero
                    # que además tengan un personaje asociado y que estén
                    # dentro de radio 20 del usuario. Es más, el if x != no es
                    # necesario.
                    pos = (aSession.user.character.x, \
                        aSession.user.character.y)
                    self.player_entered_los([session], aSession, pos, "Cute")


                (start_x, start_y) = (character.x, character.y)
                self.player_entered_los(self.session_dao.all(), session, (start_x, start_y), "Cute")

                self.session_dao.add(session)

                self.user_accepted( 
                        session = session,
                        player_initial_state = (start_x, start_y)
                        )
            else:
                self.user_rejected(host = host, port = port)

    def on_start_connection(self, (host, port)):
        self.check_protocol_version(host = host, port = port,
                    version = SERVER_VERSION, url="http://www.galaktia.com.ar")

    def on_logout_request(self, session_id):
        if session_id is not None:
            session = self.session_dao.get_by(id=session_id)
            username = session.user.name
            self.logout_response(session)
            self.char_dao.dismiss(session.user.character)

            self.user_exited(self.session_dao.all(), session, username)
            self.session_dao.delete(session)

    def on_move_dx_dy(self, session_id, (dx,dy)):
        session = self.session_dao.get_by(id=session_id)
        character = session.user.character
        (newx, newy) = ( (character.x+dx)%20, (character.y+dy)%20)

        if self.char_dao.move(character, newx, newy):
            self.player_moved(self.session_dao.all(), session, (dx, dy), (newx, newy))


def main(program, host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    here_dir = os.path.dirname(__file__)
    path = os.path.join(here_dir, '..', 'server', 'data', 'map.sqlite3')
    db_conn_str = 'sqlite:///%s' % path
    logger.info('Using database connection string: %s', db_conn_str)
    engine, metadata, session = init_db(db_conn_str)
    protocol = CamelCaseChatServer(session)
    logger.info("Starting %s", "server")
    port = int(port)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

