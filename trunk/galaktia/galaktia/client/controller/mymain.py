#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyglet
from pyglet.window import key
import math

MAP_SIZE = 21
A = 30
B = math.sqrt(3)*A
RUMBLE_DIAG = [A,B]

class GalaktiaViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self):
        super(GalaktiaViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        walter = pyglet.image.load(os.path.join(self.IMAGES_DIR, 'walter.gif'))
        self.sprites = [
            pyglet.sprite.Sprite(walter, batch=self, group=self.foreground)
        ]
        walter = self.sprites[0] # TODO: quick'n'dirty
        walter.x, walter.y = 380, 180

class GalaktiaClientWindow(pyglet.window.Window):

    def __init__(self):
        super(GalaktiaClientWindow, self).__init__(caption='Galaktia',width=1050,height=600)
        self.label = pyglet.text.Label(u'¡Bienvenido a Galaktia!',
                font_name='Arial', font_size=36, bold=True,
                x=self.width//2, y=self.height//2,
                anchor_x='center', anchor_y='center')
        self.keystate = key.KeyStateHandler()
        self.push_handlers(self.keystate)
        self.viewport = GalaktiaViewport()

    def on_draw(self):
        self.clear()
        self.draw_gl_rumble()
        self.label.draw()
        self.viewport.draw()
    
    def on_usermove(self):
        self.viewport.clear()
        self.viewport.draw()

    def draw_gl_rumble(self):
        for i in range(0,MAP_SIZE-1):
            for j in range(0,MAP_SIZE-1):
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                    ('v2f', (j*RUMBLE_DIAG[1], (i+0.5)*RUMBLE_DIAG[0], (j+0.5)*RUMBLE_DIAG[1], (i+1)*RUMBLE_DIAG[0], (j+1)*RUMBLE_DIAG[1], (i+0.5)*RUMBLE_DIAG[0], (j+0.5)*RUMBLE_DIAG[1], i*RUMBLE_DIAG[0])),
                    ('c3B', (0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 0))
                    )
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                    ('v2f', ((j+0.5)*RUMBLE_DIAG[1], (i+1)*RUMBLE_DIAG[0], (j+1)*RUMBLE_DIAG[1], (i+1.5)*RUMBLE_DIAG[0], (j+1.5)*RUMBLE_DIAG[1], (i+1)*RUMBLE_DIAG[0], (j+1)*RUMBLE_DIAG[1], (i+0.5)*RUMBLE_DIAG[0])),
                    ('c3B', (0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 0))
                    )

    def on_key_press(self, symbol, modifiers):
        print 'A key was pressed: %s %s' % (symbol, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self.dispatch_event('on_close')

    def on_text_motion(self, motion):
        STEP = A
        motion_codes = [0, -1, 1, 0] # none, lower, upper, both
        decode = lambda lower, upper: motion_codes[self.keystate[lower] \
                | (self.keystate[upper] << 1)] * STEP
        dx, dy = (decode(key.LEFT, key.RIGHT), decode(key.DOWN, key.UP))
        if dx or dy:
            walter = self.viewport.sprites[0] # TODO: quick'n'dirty
            walter.x += ((dx/STEP) * (B/2) + (dy/STEP) * (B/2))
            walter.y += (-(dx/STEP) * (A/2) + (dy/STEP) * (A/2))
            self.dispatch_event('on_draw')
            #self.on_usermove()
            
        

if __name__ == '__main__':
    window = GalaktiaClientWindow()
    window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()

