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
        
        
    
    def on_redraw(self):
        #self.grid.draw()
        self.clear()
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
            #self.dispatch_event('on_redraw')
            self.on_redraw()
            
            
class Grid():
    def __init__(self):
        self.backupChar = 'n'
        self.A = 30
        self.B = math.sqrt(3)*self.A
        self.GRID_SIZE = 21
        self.grid = []
        self.tileset = GalaktiaTileSet()
        for i in range(0,self.GRID_SIZE):
            self.grid.append([])
            for j in range(0,2*(self.GRID_SIZE)):
                self.grid[i].append('n')
                
    def from_grid_to_px(self, i, j):
        print i,j
        rx = self.GRID_SIZE * self.B
        ry = self.GRID_SIZE * self.A
        if j < 2*self.GRID_SIZE and i < self.GRID_SIZE:
            if int(j)%2 == 0:
                ry = (i-0.5)*self.A
                rx = (j/2-0.5)*self.B
            else:
                ry = (i-1)*self.A
                rx = (j/2-1)*self.B
        print int(rx),int(ry)
        return int(rx), int(ry)
    
    def from_px_to_grid(self,px,py):
        rx = 2*(self.GRID_SIZE-1)
        ry = (self.GRID_SIZE-1)
        if px < 1051 and py < 601:
            if int(px)%self.B == 0:
                rx = 2*(px//self.B)-1
                ry = (py//self.A) - 1
            else:
                rx = (px//self.B)*2
                ry = (py//self.A)
        
        return int(ry), int(rx)
    
    def draw(self):
        for i in range(0,self.GRID_SIZE):
            for j in range(0,2*(self.GRID_SIZE)):
                if self.grid[i][j] == 'n':
                    tile = self.tileset.sprites[3] 
                    tile.x, tile.y = self.from_grid_to_px(i,j)
                    tile.draw()
                 
                    
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
