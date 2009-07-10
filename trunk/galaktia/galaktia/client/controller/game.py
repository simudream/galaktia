#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyglet
from pyglet.window import key
from pyglet.gl import *
import math

from galaktia.client.model.grid import Grid

class GameViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self, x, y):
        super(GameViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        walter = pyglet.image.load(os.path.join(self.IMAGES_DIR, 'walter.gif'))
        self.sprites = [
            pyglet.sprite.Sprite(walter, batch=self, group=self.foreground)
        ]
        walter = self.sprites[0] # TODO: quick'n'dirty
        walter.x, walter.y = x,y


class GameHandler(object):

    def __init__(self, window, (x,y)):

        self.window = window
        self.viewport = GameViewport(math.sqrt(3)*30/2, 30/2)
        self.grid = Grid()
        
        
    def on_draw(self):
        self.clear()
        self.grid.draw()
        #self.label.draw()
        self.viewport.draw()
        
    def on_text(self, text):
        pass

    def on_key_press(self, symbol, modifiers):
        # print 'A key was pressed: %s %s' % (symbol, modifiers)
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
            walter.x, walter.y = self.grid.moveSprite(walter.x,walter.y,math.floor(dx/STEP),math.floor(dy/STEP))  
            #self.dispatch_event('on_redraw')
            #self.redraw()
            
            

    

if __name__ == '__main__':
    window = GalaktiaClientWindow()
    pyglet.app.run()
