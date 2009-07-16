#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, logging

from pyglet.window import key
from pyglet.gl import *

from galaktia.client.controller.chat import ChatHandler
from galaktia.client.controller.login import LoginHandler
from galaktia.server.protocol.interface import ClientProtocolInterface


import pyglet

from twisted.internet import reactor
from twisted.python import log

logger = logging.getLogger(__name__)




CLIENT_VERSION = "0.1"

class GalaktiaWindow(pyglet.window.Window, ClientProtocolInterface):

    def __init__(self, (host, port)):
        
        pyglet.window.Window.__init__(self, caption='Galaktia')
        ClientProtocolInterface.__init__(self, (host, port))
        self.keystate = key.KeyStateHandler()
        self.push_handlers(self.keystate)

    def set_window_handler(self, handler):
        self.handler = handler
    def change_handler(self,Hclass):
        nh = Hclass(self)
        self.set_window_handler(nh)


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
    def on_resize(self,width, height):
        self.handler.on_resize(width, height)
    def on_close(self):
        reactor.stop()
        sys.exit(0)
        return True



    # PROTOCOL INTERFACE
    def on_greet(self):
        self.start_connection()
    def on_check_protocol_version(self, version, url):
        if version != CLIENT_VERSION:
            raise ValueError, "Version muy vieja del cliente, necesitas la %s. " % version + \
                "Te la podes bajar de %s" % url
        else:
            logger.info("Client Version OK :D")

    def on_user_accepted(self, session_id, (x, y)):
        logger.info("User accepted! session_id = %s, starting coords = (%d, %d)." % (session_id, x, y) +\
            "Try opening other clients at the same time :D...")
        self.session_id = session_id
        self.change_handler(ChatHandler)

    def on_user_joined(self, username):
        logger.info("User joined: %s" % username) 

    def on_user_rejected(self):
        logger.info("User was rejected by server")


    def on_someone_said(self, message, username):
        raise NotImplementedError
    def on_player_entered_los(self, session_id, (x,y), description):
        raise NotImplementedError
    def on_player_moved(self, other_session_id, (dx,dy), (x,y)):
        raise NotImplementedError
    def on_user_exited(self, session_id):
        raise NotImplementedError
    def on_logout_response(self):
        logger.info("Client application terminated")
        sys.exit(0)





   
    
def main(program, host='127.0.0.1', port=6414):
    
    window = GalaktiaWindow((host,port))
    login_handler = LoginHandler(window)
    window.set_window_handler(login_handler)



    log_level = logging.DEBUG
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting Galaktia Client')

    listen_port = 0 # dinamically assign client port

    import threading
    

    # We'll run twisted in a separate thread
    class TwistedThread(threading.Thread):
        def run(self):
            reactor.listenUDP(listen_port, window)
            reactor.run()

    TwistedThread().start()
    pyglet.app.run()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    main(*sys.argv)


