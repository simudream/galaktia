#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, logging

from pyglet.window import key
from pyglet.gl import *

from galaktia.client.controller.game import GameHandler
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

    # TERMINAL 
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
        return True



    # PROTOCOL 
    def on_greet(self):
        self.start_connection()
    def on_check_protocol_version(self, version, url):
        if version != CLIENT_VERSION:
            raise ValueError, "Version muy vieja del cliente, necesitas la %s. " % version + \
                "Te la podes bajar de %s" % url
        else:
            print "Client Version O.K."

    def on_user_accepted(self, session_id, (x, y)):
        self.session_id = session_id
        new_handler = GameHandler(self, (x,y))
        self.set_window_handler(new_handler)

    def on_user_rejected(self):
        raise NotImplementedError
    def on_someone_said(self, message, username):
        raise NotImplementedError


    def on_player_entered_los(self, session_id, (x,y), description):
        raise NotImplementedError
    def on_user_joined(self, username):
        raise NotImplementedError
    def on_player_moved(self, other_session_id, (dx,dy), (x,y)):
        raise NotImplementedError
    def on_user_exited(self, session_id):
        raise NotImplementedError
    def on_logout_response(self):
        raise NotImplementedError





   
    
def main(program, host='127.0.0.1', port=6414):
    
    window = GalaktiaWindow((host,port))
    login_handler = LoginHandler(window)
    window.set_window_handler(login_handler)


    log_level = logging.DEBUG
    logging.basicConfig(stream=sys.stderr, level=log_level)
    logger.info('Starting Galaktia Client')
    
    listen_port = 0 # dinamically assign client port
    
    # This is one possible way:
    #reactor.listenUDP(listen_port, window)
    #reactor.callInThread(pyglet.app.run)
    #reactor.run()
    #pyglet.app.run()
    
    
    # This is another...
    import threading

    class PygletThread(threading.Thread):
        def run(self):
            pyglet.app.run()
            
    class TwistedThread(threading.Thread):
        def run(self):
            reactor.listenUDP(listen_port, window)
            reactor.run()

    PygletThread().start()
    # Try commenting the line below...
    # pyglet isn't functioning either way.
    TwistedThread().start()

if __name__ == '__main__': # This is how to run a main program
    reload(sys); sys.setdefaultencoding('utf-8')
    main(*sys.argv)


