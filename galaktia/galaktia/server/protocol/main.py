#!/usr/bin/env python
# -*- coding: utf-8 -*-

from galaktia.server.protocol.interface import ServerProtocolInterface
from galaktia.server.persistence.dao import StationaryDAO, CharacterDAO
from galaktia.server.persistence.orm import Stationary, Character, init_db

from random import randint
from twisted.internet import reactor
from twisted.python import log
import sys, logging


logger = logging.getLogger(__name__)


SERVER_VERSION = "0.2"

class CamelCaseChatServer(ServerProtocolInterface):
    """ Implementation of a simple chat server """

    def __init__(self, session):
        self.session=session
            # Database session. Please, do not touch :P
        ServerProtocolInterface.__init__(self)
        self.n_users = 0
        self.char_dao = CharacterDAO(session)
        self.stat_dao = StationaryDAO(session)
            # Useless ATM.

    def on_say_this(self, talking_user_id, message):
        self.someone_said(
                session_list = self.sessions.keys(),
                username = self.sessions[talking_user_id]['username'],
                message = message
                )

    def on_request_user_join(self, host, port, username):
            # TODO: instanciar el usuario en la base de datos
            session_id = self._generate_session_id(username)
            char = self.char_dao.get_by(name=username)
            
            if session_id not in self.sessions and not char:
                self.user_joined( username = username,
                            session_list = self.sessions.keys())
                self._store_session(session_id, host, port, username)
                self.sessions[session_id]['character'] = char
                
                if not self.sessions[session_id]['character']:
                    walter=Character()
                    walter.name=username
                    walter.x, walter.y = (randint(0,9),randint(0,9))
                    walter.z=0
                    walter.level=42
                    self.char_dao.add(walter)
                    self.sessions[session_id]['character'] = walter
                    self.char_dao.session.flush()
                        # This should be done by another thread, watching the
                        # changes and commiting them.
                
                # for aSession in filter(lambda x: x != session_id, self.sessions):
                for aSession in (x for x in self.sessions if \
                        self.sessions[x]['character'] in \
                        self.char_dao.get_near(self.sessions[session_id]['character'],
                            radius=20)):
                    # Explicación: pide todas las sessions (no propias), pero
                    # que además tengan un personaje asociado y que estén
                    # dentro de radio 20 del usuario. Es más, el if x != no es
                    # necesario.
                    self.player_entered_los([session_id], aSession, \
                            self.sessions[aSession]['pos'], "Cute")


                (start_x, start_y) = (self.sessions[session_id]['character'].x, \
                        self.sessions[session_id]['character'].y)
                self.player_entered_los(self.sessions.keys(), session_id, (start_x, start_y), "Cute")

                self.sessions[session_id]['pos'] = (start_x, start_y)
                self.user_accepted( 
                        session_id = session_id,
                        player_initial_state = (start_x, start_y)
                        )
            else:
                self.user_rejected( host = host, port = port )

    def on_start_connection(self, (host, port)):
        self.check_protocol_version(host = host, port = port,
                    version = SERVER_VERSION, url="http://www.galaktia.com.ar")

    def on_logout_request(self, session):
        if session is not None:
            username = self.sessions[session]['username']
            self.logout_response(session)
            
            self.char_dao.delete(self.sessions[session]['character'])
            del self.sessions[session]
            
            self.user_exited(self.sessions.keys(), session, username)

    def on_move_dx_dy(self, session_id, (dx,dy)):
        character = self.sessions[session_id]['character']
        (newx, newy) = ( (character.x+dx)%20, (character.y+dy)%20)
        if self.char_dao.move(character,newx,newy):
            self.player_moved(self.sessions.keys(), session_id, (dx,dy), (newx,newy))

    def _generate_session_id(self,username):
        """ Assigns a unique identifier to the requested username """
        self.n_users +=1
        return self.n_users

    def _store_session(self,session_id, host, port, username):
        self.sessions[session_id] = {
                'host' : host,
                'port' : port,
                'username' : username
                }


def main(program, host='127.0.0.1', port=6414, session=None):
    """ Main program: Starts a chat client or server on given host:port """
    port = int(port)
    log_level = logging.DEBUG
    protocol = CamelCaseChatServer(session)
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info("Starting %s", "server")
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    a,b,c = init_db(db_connection_string="sqlite:///../persistence/map.sqlite3")
    print c
    # main(*sys.argv)
    main(session=c,*sys.argv)
