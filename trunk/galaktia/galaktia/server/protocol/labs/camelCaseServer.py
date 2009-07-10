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

    def on_say_this(self, talking_user, message):
        self.someone_said(
                session_list = self.sessions.keys(),
                username = talking_user,
                message = message.title()
                )

    def on_request_user_join(self, host, port, username):
            # TODO: instanciar el usuario en la base de datos
            session_id = self._generate_session_id(username)
            if session_id not in self.sessions:
                self._store_session(session_id, host, port, username)
                self.user_joined( username = username,
                            session_list = self.sessions.keys())

                self.user_accepted( 
                        session_id = session_id,
                        player_initial_state = (randint(1,10),randint(1,10))
                        )
            else:
                self.user_rejected( host = host, port = port)

    def on_start_connection(self, (host, port)):
        self.check_protocol_version(host = host, port = port,
                    version = SERVER_VERSION, url="http://www.galaktia.com.ar")

    def on_logout_request(self, session):
        username = self.sessions[session]['username']
        self.logout_response(session)
        del self.sessions[session]
        self.user_exited(self.sessions.keys(), username)

    def on_move_dx_dy(self, session_id, (dx,dy)):
        raise NotImplementedError

    def _generate_session_id(self,username):
        """ Assigns a unique identifier to the requested username """
        return str(username)

    def _store_session(self,session_id, host, port, username):
        self.sessions[session_id] = {
                'host' : host,
                'port' : port,
                'username' : username
                }


def main(program, endpoint='server', host='127.0.0.1', port=6414):
    """ Main program: Starts a chat client or server on given host:port """
    
    log_level = logging.DEBUG
    protocol = CamelCaseChatServer()
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info("Starting %s", endpoint)
    reactor.listenUDP(port, protocol)
    reactor.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    # log.startLogging(sys.stderr) # enables Twisted logging
    main(*sys.argv)

