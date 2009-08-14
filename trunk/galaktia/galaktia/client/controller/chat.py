#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyglet, os
from galaktia.client.controller.widget import TextWidget, ChatWidget
from pyglet.gl import glViewport, glMatrixMode, glLoadIdentity, glOrtho
import pyglet.gl as gl

class LoginViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self):
        super(LoginViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)

ARROW_KEY_TO_VERSOR = {
    65362 : (0,1),
    65361 : (-1,0),
    65364 : (0,-1),
    65363 : (1,0)
}



class ChatHandler():
    grid_size = 20
    PADDING_LEFT = 18
    PADDING_DOWN = 5
    MAP_DIM = 20

    def __init__(self, window, username, (x, y), surroundings):
        self.viewport = LoginViewport()
        self.window = window
        self.welcomeLabel = pyglet.text.Label(u'¡WalterLand!',
                font_name='Arial', font_size=36, bold=True,
                x=self.window.width//4, y=self.window.height-40,
                anchor_x='center', anchor_y='center')
        self.usernameLabel = pyglet.text.Label(u''+username,
                font_name='Arial', font_size=12, bold=True,
                x=10, y=24,
                anchor_x='left', anchor_y='center')
        self.chatInformLabel = pyglet.text.Label(u'Press enter to chat',
                font_name='Arial', font_size=12, bold=True,
                x=10, y=24,
                anchor_x='left', anchor_y='center')
        self.walter = pyglet.image.load(os.path.join(self.window.IMAGES_DIR, 'walter.gif'))
        self.walter2 = pyglet.image.load(os.path.join(self.window.IMAGES_DIR, 'walter2.gif'))
        self.piso = pyglet.image.load(os.path.join(self.window.IMAGES_DIR, 'piso.gif'))
        self.pared = pyglet.image.load(os.path.join(self.window.IMAGES_DIR, 'pared.gif'))


        self.widgets = [
            TextWidget('', 130, 10, int(self.window.width//3), self.viewport),
        ]
        self.chat_widget = ChatWidget()

        # sound stuff... uncomment in the future
        #self.sound_user_connected = pyglet.resource.media('bass.wav',streaming=False)
        #self.sound_chat = pyglet.resource.media('doub.wav',streaming=False)
        #music = pyglet.resource.media('music.mp3')
        #player = pyglet.media.Player()
        #player.queue(music)
        #player.eos_action = 'loop'
        #player.play()

        self.text_cursor = self.window.get_system_mouse_cursor('text') 
        self.focus = None

        self.mapa = [(t[0],t[1]) for t in surroundings]

    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.window.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.window.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
                break
        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            if text != '\r':
                self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)
        else:
            try:
                (dx,dy) = ARROW_KEY_TO_VERSOR[motion]
                self.window.move_dx_dy((dx,dy))
            except:
                pass

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)

    def on_close(self):
        self.window.logout_request()

    def on_draw(self):
        self.window.clear()
        self.welcomeLabel.draw()
        if self.focus:
            self.viewport.draw()
            self.usernameLabel.draw()
        else:
            self.chatInformLabel.draw()
        for x in xrange(self.MAP_DIM):
            for y in xrange(self.MAP_DIM):
                self.piso.blit(self.grid_size*(x+self.PADDING_LEFT),self.grid_size*(y+self.PADDING_DOWN))

        self.chat_widget.draw()

        for walter in self.window.peers:
            x,y = self.window.peers[walter]
            if self.window.session.id == walter:
                self.walter2.blit(self.grid_size*(x+self.PADDING_LEFT),self.grid_size*(y+self.PADDING_DOWN))
            else:
                self.walter.blit(self.grid_size*(x+self.PADDING_LEFT),self.grid_size*(y+self.PADDING_DOWN))
        for x,y in self.mapa:
            self.pared.blit(self.grid_size*(x+self.PADDING_LEFT),self.grid_size*(y+self.PADDING_DOWN))

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.window.dispatch_event('on_close')
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.NUM_ENTER):
            if self.focus:
                self.chatear()
                self.focus = None
            else:
                self.set_focus(self.widgets[0])
                chatbox = self.widgets[0]
                chatbox.empty()

    def on_key_release(self,symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            if self.focus:
                pass
            else:
                self.focus = None

    def on_resize(self,width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

    def on_someone_said(self, username, message):
        #self.sound_chat.play()
        self.chat_widget.show_message("%s: %s" % (username, message))
        
    def on_user_joined(self, username):
        #self.sound_user_connected.play()
        m = "User joined: %s" % username
        self.chat_widget.show_message(m)

    def on_user_exited(self,session_id, username):
        #self.sound_user_connected.play()
        m = "User left room: %s" % username
        self.chat_widget.show_message(m)
        del self.window.peers[session_id]

    def chatear(self):
        chatbox = self.widgets[0]
        message = chatbox.text()
        self.window.say_this(message)