#!/usr/bin/python
# -*- coding: utf-8 -*-

from galaktia.client.controller.pygletreactor import install
reactor = install()

import os, sys, logging

import pyglet
pyglet.options['audio'] = ('openal', 'alsa')
from pyglet.gl import glViewport, glMatrixMode, glLoadIdentity, glOrtho
from twisted.internet import reactor
from twisted.python import log

from galaktia.client.controller.game import GameHandler
from galaktia.client.controller.login import LoginHandler
from galaktia.client.paths import IMAGES_DIR, SOUND_DIR
from galaktia.protocol.interface import ClientProtocolInterface

from galaktia.protocol.codec import PublicKey

logger = logging.getLogger(__name__)


class GalaktiaWindow(pyglet.window.Window, ClientProtocolInterface):

    def __init__(self, (host, port)):

        pyglet.window.Window.__init__(self,  width=800, height=600,caption='Galaktia')
        ClientProtocolInterface.__init__(self, ClientSessionDAO(), (host, port))
        self.keystate = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keystate)

        icon = pyglet.image.load(os.path.join(IMAGES_DIR, 'logo.jpg'))
        self.set_icon(icon)

        # jajaja esto es muy hacker!
        pyglet.resource.path = [ SOUND_DIR ]
        pyglet.resource.reindex()

        self.session = self.session_dao.get(0)

    def set_window_handler(self, handler):
        self.handler = handler



    # USER TERMINAL 
    def on_mouse_motion(self, x, y, dx, dy):
        self.handler.on_mouse_motion(x, y, dx, dy)
    def on_mouse_press(self, x, y, button, modifiers):
        self.handler.on_mouse_press(x, y, button, modifiers)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.handler.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    def on_text(self, text):
        self.handler.on_text(text)
    def on_text_motion(self, motion):
        self.handler.on_text_motion(motion)
    def on_text_motion_select(self, motion):
        self.handler.on_text_motion_select(motion)
    def on_draw(self):
        self.handler.on_draw()
    def on_key_press(self, symbol, modifiers):
        self.handler.on_key_press(symbol,modifiers)
    def on_key_release(self,symbol, modifiers):
        self.handler.on_key_release(symbol,modifiers)
    def on_resize(self,width, height):
        self.handler.on_resize(width, height)
    def on_close(self):
        self.handler.on_close()

    # PROTOCOL INTERFACE
    def on_greet(self):
        self.start_connection()

    def on_check_protocol_version(self, session_id, version, url):
        m = "Checking if client version is OK..."
        logger.info(m)
        self.handler.on_check_protocol_version(session_id, version, url)

    def on_user_accepted(self, username, (x, y), surroundings):
        logger.info("User accepted! starting coords = (%d, %d)." % (x, y))

        self.session = ClientSession(self.session.id, username.ljust(16))
        self.session_dao.set(self.session)

        new_handler = GameHandler(self, username, (x, y), surroundings)
        self.set_window_handler(new_handler)

    def on_user_joined(self, username):
        m = "User joined: %s" % username
        logger.info(m)
        self.handler.on_user_joined(username)

    def on_user_exited(self, session_id, username):
        m = "User exited: %s" % username
        logger.info(m)
        self.handler.on_user_exited(session_id, username)

    def on_user_rejected(self):
        m = "User was rejected by server"
        logger.info(m)
        self.handler.on_user_rejected()

    def on_someone_said(self, username, message):
        m = u"%s: %s" % (str(username), str(message))
        logger.info(m)
        self.handler.on_someone_said(username, message)

    def on_player_entered_los(self, session_id, (x,y), description):
        m = "New player entered game... he's %s." % description
        logger.info(m)
        self.handler.on_player_entered_los(session_id, (x,y), description)

    def on_player_moved(self, other_session_id, (dx,dy), (x,y)):
        m = "Player %s moved to %s" % (str(other_session_id),str((x,y)))
        logger.info(m)
        self.handler.on_player_moved(other_session_id, (dx,dy), (x,y))

    def on_logout_response(self):
        logger.info("Client application terminated")
        self.exit()

    def exit(self):
        reactor.stop()
        return True
    
    def connectionRefused(self):
        m = "Connection to server was refused"
        logger.info(m)
        self.handler.on_connection_refused()

class ClientSession:
    """ Session stub to be used in the protocol layer """

    def __init__(self, id, key):
        self.id = id
        self.key = key
        self.host = None
        self.port = None

    def get_encryption_key(self):
        return self.key

class ClientSessionDAO:
    """ SessionDAO stub to be used in the protocol layer """

    def __init__(self):
        self.session = ClientSession(0, PublicKey)

    def set(self, session):
        self.session = session

    def get(self, id):
        self.session.id = id
        return self.session


def main(program, host='127.0.0.1', port=6414):

    window = GalaktiaWindow((host,port))
    login_handler = LoginHandler(window)
    window.set_window_handler(login_handler)

    log_level = logging.DEBUG
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting Galaktia Client')

    listen_port = 0 # dinamically assign client port
    reactor.listenUDP(listen_port, window)
    reactor.run()



if __name__ == '__main__':
    print 'Usage: python -m galaktia.client [server host] [server port]'
    main(*sys.argv)

