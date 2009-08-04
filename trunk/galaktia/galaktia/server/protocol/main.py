#!/usr/bin/env python
# -*- coding: utf-8 -*-




from galaktia.server.protocol.interface import ServerProtocolInterface

from random import randint
from twisted.internet import reactor
from twisted.python import log
import sys, logging


logger = logging.getLogger(__name__)


SERVER_VERSION = "0.1"

class CamelCaseChatServer(ServerProtocolInterface):
    """ Implementation of a simple chat server """

    def __init__(self):
        ServerProtocolInterface.__init__(self)
        self.n_users = 0

    def on_say_this(self, talking_user_id, message):
        self.someone_said(
                session_list = self.sessions.keys(),
                username = self.sessions[talking_user_id]['username'],
                message = message
                )

    def on_request_user_join(self, host, port, username):
            # TODO: instanciar el usuario en la base de datos
            session_id = self._generate_session_id(username)
            if session_id not in self.sessions:
                self.user_joined( username = username,
                            session_list = self.sessions.keys())

                self._store_session(session_id, host, port, username)

                (start_x, start_y) = (randint(0,9),randint(0,9))
                self.player_entered_los(self.sessions.keys(), session_id, (start_x, start_y), "Cute")

                self.sessions[session_id]['pos'] = (start_x, start_y)
                self.user_accepted( 
                        session_id = session_id,
                        player_initial_state = (start_x, start_y)
                        )
            else:
                self.user_rejected( host = host, port = port)

    def on_start_connection(self, (host, port)):
        self.check_protocol_version(host = host, port = port,
                    version = SERVER_VERSION, url="http://www.galaktia.com.ar")

    def on_logout_request(self, session):
        if session is not None:
            username = self.sessions[session]['username']
            self.logout_response(session)
            del self.sessions[session]
            self.user_exited(self.sessions.keys(), username)

    def on_move_dx_dy(self, session_id, (dx,dy)):
        (x,y) = self.sessions[session_id]['pos']
        (newx, newy) = ( (x+dx)%10, (y+dy)%10)
        self.sessions[session_id]['pos'] = (newx, newy)
        player_moved(self, self.sessions.keys(), session_id, (dx,dy), (newx,newy))

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


def main(program, host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    port = int(port)
    log_level = logging.DEBUG
    protocol = CamelCaseChatServer()
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info("Starting %s", "server")
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

