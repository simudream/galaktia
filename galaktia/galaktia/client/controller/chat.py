#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyglet, os
from galaktia.client.controller.widget import TextWidget
from pyglet.gl import glViewport, glMatrixMode, glLoadIdentity, glOrtho
import pyglet.gl as gl

from galaktia.client.controller.game import GameHandler

class LoginViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self):
        super(LoginViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)


class ChatHandler():

    def __init__(self, window, username):
        self.viewport = LoginViewport()
        self.window = window
        self.welcomeLabel = pyglet.text.Label(u'¡Super Chat!',
                font_name='Arial', font_size=36, bold=True,
                x=self.window.width//4, y=self.window.height-40,
                anchor_x='center', anchor_y='center')
        self.usernameLabel = pyglet.text.Label(u''+username,
                font_name='Arial', font_size=12, bold=True,
                x=10, y=24,
                anchor_x='left', anchor_y='center')
        self.widgets = [
            TextWidget('', 130, 10, int(self.window.width//1.5), self.viewport),
        ]
        
        self.messages = []
        
        self.text_cursor = self.window.get_system_mouse_cursor('text') 
        self.focus = None
        self.set_focus(self.widgets[0])
    
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
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)
      
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
        self.viewport.draw()
        self.welcomeLabel.draw()
        self.usernameLabel.draw()
        for message in self.messages:
            message.draw()



    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.window.dispatch_event('on_close')
        elif symbol == pyglet.window.key.ENTER:
            self.chatear()
    def on_key_release(self,symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            chatbox = self.widgets[0]
            chatbox.empty()
            
    def on_resize(self,width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)
    
    def on_someone_said(self, username, message):
        self.show_message("%s: %s" % (username, message))

    def show_message(self, message):
        for label in self.messages:
            label.y += 20
        self.messages.append(pyglet.text.Label(u''+message,
                font_name='Arial', font_size=12, bold=True,
                x=50, y=40+20,
                anchor_x='left', anchor_y='center'))

    def chatear(self):
        chatbox = self.widgets[0]
        message = chatbox.text()
        self.window.say_this(message)