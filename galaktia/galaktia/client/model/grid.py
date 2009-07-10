#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import pyglet
import os
from random import randint


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
            
class Tile(dict):
    
    def __init__(self):
        self['terrain'] = randint(1,8)
        self['content'] = 'n'
        self.update({})

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
                self.grid[i].append(Tile())
                
    def from_grid_to_px(self, i, j):
        # print i,j
        rx = self.GRID_SIZE * self.B
        ry = self.GRID_SIZE * self.A
        if j < 2*self.GRID_SIZE and i < self.GRID_SIZE:
            if int(j)%2 == 0:
                ry = (i-0.5)*self.A
                rx = (j/2-0.5)*self.B
            else:
                ry = (i-1)*self.A
                rx = (j/2-1)*self.B
        #print int(rx),int(ry)
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
                if self.grid[i][j]['content'] == 'n':
                    tile_id = self.grid[i][j]['terrain']
                    tile = self.tileset.sprites[tile_id] 
                    tile.x, tile.y = self.from_grid_to_px(i,j)
                    tile.draw()
                 
                    
    def moveSprite(self, x, y, dx, dy):
        rx = x
        ry = y
        i , j = self.from_px_to_grid(rx,ry)
        self.grid[i][j]['content'] = self.backupChar
        rx = ((dx) * (self.B/2) + (dy) * (self.B/2)) + x
        ry = (-(dx) * (self.A/2) + (dy) * (self.A/2)) + y
        i , j = self.from_px_to_grid(rx,ry)
        self.backupChar = self.grid[i][j]['content']
        self.grid[i][j]['content'] = 'n'
        return rx , ry
        
        
        