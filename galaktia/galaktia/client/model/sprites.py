#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import pyglet.media
from pyglet.gl import glEnable,GL_BLEND,glBlendFunc,GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA

from galaktia.client.paths import IMAGES_DIR

class GameView(object):
    def __init__(self, map_dim, tile_width, tile_height, padding_left, padding_down, surroundings):
        self.tile_width = tile_width
        self.tile_height = tile_height

        self.padding_left = padding_left
        self.padding_down = padding_down

        self.walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'walter.png'))
        self.red_walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'red_walter.png'))
        self.piso = pyglet.image.load(os.path.join(IMAGES_DIR, 'piso.png'))
        self.pared = pyglet.image.load(os.path.join(IMAGES_DIR, 'pared.png'))
        
        self.mapa = [Pared((t[0],t[1]), self.pared) for t in surroundings]
        self.baldosas = []
        for x in xrange(map_dim):
            for y in xrange(map_dim):
                self.baldosas.append(Baldosa((x,y), self.piso))
        self.peers = {}
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.center_walter = {'x':0, 'y':0}
	self.own_walter = None

    def draw(self):
	self.center_walter['x'] = self.own_walter.x
	self.center_walter['y'] = self.own_walter.y

        for baldosa in self.baldosas:
            baldosa.draw(self.tile_width, self.tile_height, \
                         self.padding_left, self.padding_down, self.center_walter)
        
        for pared in self.mapa:
            pared.draw(self.tile_width, self.tile_height, \
                         self.padding_left, self.padding_down, self.center_walter)
        
        for aSession in self.peers:
            walter = self.peers[aSession]
            if walter == self.own_walter:
                walter.draw(self.tile_width, self.tile_height, \
			    self.padding_left, self.padding_down, self.center_walter)
            else:
                walter.draw(self.tile_width, self.tile_height, \
                            self.padding_left, self.padding_down, self.center_walter)

    def delete_player(self, session_id):
        del self.peers[session_id]

    def add_player(self, session_id, (x,y), description, is_me):
        image = self.red_walter if is_me else self.walter
        player = Walter((x,y), description, image)
        self.peers[session_id] = player
        if is_me:
            self.center_walter['x'] = x
            self.center_walter['y'] = y
	    self.own_walter = player

class Sprite(object):
    def __init__(self, (x,y), image):
        self.x, self.y = x,y
        self.image = image
    def draw(self, tile_width, tile_height, padding_left, padding_down, center):
        iso_x = (self.y - center['y'] + self.x - center['x'])*0.91
        iso_y = (self.y - center['y'] - self.x + center['x'])*0.91
        self.image.blit(tile_width*iso_x+padding_left, tile_height*iso_y+padding_down)


class Walter(Sprite):

    def __init__(self, (x,y), description, image):
        self.name = description
        super(Walter, self).__init__((x,y), image)

    def set_position(self,x,y):
        self.x, self.y = x, y


class Baldosa(Sprite):
    pass
class Pared(Sprite):
    pass
