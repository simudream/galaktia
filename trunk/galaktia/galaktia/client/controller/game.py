#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import pyglet
from pyglet.gl import glViewport, glMatrixMode, glLoadIdentity, glOrtho
import pyglet.gl as gl

from galaktia.client.controller.widget import TextWidget, ChatWidget
from galaktia.client.model.sprites import GameView
from galaktia.client.paths import IMAGES_DIR


class GameViewport(pyglet.graphics.Batch):

    def __init__(self):
        super(GameViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)

ARROW_KEY_TO_VERSOR = {
    pyglet.window.key.UP : (-0.5,0.5),
    pyglet.window.key.LEFT : (-0.5,-0.5),
    pyglet.window.key.DOWN : (0.5,-0.5),
    pyglet.window.key.RIGHT : (0.5,0.5)
}


class GameHandler():

    MAP_DIM = 20
    TILE_WIDTH = 51 / 2.0
    TILE_HEIGHT = 33 / 2.0

    def __init__(self, window, username, (x, y), surroundings, screen_parameters):
        self.viewport = GameViewport()
        self.window = window

        self.keyboard = pyglet.window.key.KeyStateHandler()
        self.keyboard[pyglet.window.key.UP] = self.keyboard[pyglet.window.key.DOWN] = \
            self.keyboard[pyglet.window.key.LEFT] = self.keyboard[pyglet.window.key.RIGHT] = False
        self.window.push_handlers(self.keyboard)

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

        self.game_view = GameView(self.MAP_DIM,
            self.TILE_WIDTH, self.TILE_HEIGHT,
            (screen_parameters[0]-self.TILE_WIDTH)/2,
            (screen_parameters[1]-self.TILE_HEIGHT)/2,
            surroundings)


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
        elif motion in ARROW_KEY_TO_VERSOR:
            (dx,dy) = ARROW_KEY_TO_VERSOR[motion]
            dx, dy = 0, 0
            for arrow_key in ARROW_KEY_TO_VERSOR:
                if self.keyboard[arrow_key]:
                    versor_tuple = ARROW_KEY_TO_VERSOR[arrow_key]
                    dx += versor_tuple[0]
                    dy += versor_tuple[1]
            dx, dy = int(round(dx)), int(round(dy))
            self.window.move_dx_dy((dx,dy))


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
        self.game_view.draw()
        self.welcomeLabel.draw()
        if self.focus:
            self.viewport.draw()
            self.usernameLabel.draw()
        else:
            self.chatInformLabel.draw()

        self.chat_widget.draw()


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

    def on_someone_said(self, username, message):
        #self.sound_chat.play()
        self.chat_widget.show_message("%s: %s" % (username, message))

    def on_user_joined(self, username):
        #self.sound_user_connected.play()
        self.chat_widget.show_message("User joined: %s" % username)

    def on_user_exited(self,session_id, username):
        #self.sound_user_connected.play()
        self.chat_widget.show_message("User left room: %s" % username)
        self.game_view.delete_player(session_id)

    def on_player_entered_los(self, session_id, (x,y), description):
        is_me = True if self.window.session.id == session_id else False
        self.game_view.add_player(session_id, (x,y), description, is_me)

    def on_player_moved(self, other_session_id, (dx,dy), (x,y)):
        self.game_view.peers[other_session_id].set_position(x,y)

    def chatear(self):
        chatbox = self.widgets[0]
        message = chatbox.text()
        self.window.say_this(message)
