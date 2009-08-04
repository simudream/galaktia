#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyglet
from pyglet.window import key
from pyglet.gl import *
import math

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
        walter.x, walter.y = math.sqrt(3)*30/2, 30/2

class GalaktiaTileSet(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images', 'tiles')

    def __init__(self):
        super(GalaktiaTileSet, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.sprites = []
        for i in range(1,9):
            tile = pyglet.image.load(os.path.join(self.IMAGES_DIR, str(i)+'.png'))
            self.sprites.append(pyglet.sprite.Sprite(tile, batch=self, group=self.foreground))

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
        self.grid = Grid()

    def on_draw(self):
        self.clear()
        self.grid.draw()
        self.label.draw()
        self.viewport.draw()

    def on_usermove(self):
        self.grid.draw()
        self.viewport.draw()


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
            walter.x, walter.y = self.grid.moveSprite(walter.x,walter.y,math.floor(dx/STEP),math.floor(dy/STEP))  
            self.dispatch_event('on_draw')
            #self.viewport.draw()
            
            
class Grid():
    def __init__(self):
        self.backupChar = 'n'
        self.A = 30
        self.B = math.sqrt(3)*self.A
        self.GRID_SIZE = 21
        self.grid = []
        self.tileset = GalaktiaTileSet()
        for i in range(0,self.GRID_SIZE-1):
            self.grid.append([])
            for j in range(0,self.GRID_SIZE-1):
                self.grid[i].append('n')
                self.grid[i].append('n')

    def from_grid_to_px(self, x, y):
        rx = self.GRID_SIZE * self.B
        ry = self.GRID_SIZE * self.A
        if x < 2*self.GRID_SIZE and y < self.GRID_SIZE:
            if x%2 == 0:
                ry = (y+0.5)*self.A
                rx = (x+0.5)*self.B
            else:
                ry = (y+1)*self.A
                rx = (x+1)*self.B
        return rx, ry
    
    def from_px_to_grid(self,px,py):
        rx = self.GRID_SIZE
        ry = 2*self.GRID_SIZE
        if px < 10000 and py < 10000:
            if int(py)%self.A == 0:
                rx = 2*math.floor(px/self.B)-1
                ry = math.floor(py/self.A) - 1
            else:
                rx = math.floor(px/self.B)*2
                ry = math.floor(py/self.A)
        
        return int(rx), int(ry)
    
    def draw(self):
        for i in range(0,self.GRID_SIZE-1):
            for j in range(0,self.GRID_SIZE-1):
                if self.grid[i][2*j] == 'n':
                    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                        ('v2f', (j*self.B, (i+0.5)*self.A, (j+0.5)*self.B, (i+1)*self.A, (j+1)*self.B, (i+0.5)*self.A, (j+0.5)*self.B, i*self.A)),
                        ('c3B', (0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255))
                        )
                if self.grid[i][2*j+1] == 'n':
                    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                        ('v2f', ((j+0.5)*self.B, (i+1)*self.A, (j+1)*self.B, (i+1.5)*self.A, (j+1.5)*self.B, (i+1)*self.A, (j+1)*self.B, (i+0.5)*self.A)),
                        ('c3B', (0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255))
                        )
                 
                    
    def moveSprite(self, x, y, dx, dy):
        rx = x
        ry = y
        i , j = self.from_px_to_grid(rx,ry)
        self.grid[i][j] = self.backupChar
        rx = ((dx) * (self.B/2) + (dy) * (self.B/2)) + x
        ry = (-(dx) * (self.A/2) + (dy) * (self.A/2)) + y
        i , j = self.from_px_to_grid(rx,ry)
        self.backupChar = self.grid[i][j]
        self.grid[i][j] = 'n'
        return rx , ry
    

if __name__ == '__main__':
    window = GalaktiaClientWindow()
    window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()
