#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyglet
from pyglet.window import key

class GalaktiaViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self):
        super(GalaktiaViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        image = pyglet.image.load(os.path.join(self.IMAGES_DIR, 'walter.gif'))
        self.sprites = [
            pyglet.sprite.Sprite(image, batch=self, group=self.foreground)
        ]
        walter = self.sprites[0] # TODO: quick'n'dirty
        walter.x, walter.y = 380, 180

class GalaktiaClientWindow(pyglet.window.Window):

    def __init__(self):
        super(GalaktiaClientWindow, self).__init__(caption='Galaktia')
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

    def draw_gl_rumble(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (300, 300, 500, 200, 300, 100, 100, 200)),
                ('c3B', (0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 0))
        )

    def on_key_press(self, symbol, modifiers):
        print 'A key was pressed: %s %s' % (symbol, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self.dispatch_event('on_close')

    def on_text_motion(self, motion):
        STEP = 20
        motion_codes = [0, -1, 1, 0] # none, lower, upper, both
        decode = lambda lower, upper: motion_codes[self.keystate[lower] \
                | (self.keystate[upper] << 1)] * STEP
        dx, dy = (decode(key.LEFT, key.RIGHT), decode(key.DOWN, key.UP))
        if dx or dy:
            walter = self.viewport.sprites[0] # TODO: quick'n'dirty
            walter.x += dx
            walter.y += dy
            self.dispatch_event('on_draw')

if __name__ == '__main__':
    window = GalaktiaClientWindow()
    window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()

