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

    def draw(self):

        for baldosa in self.baldosas:
            baldosa.draw(self.tile_width, self.tile_height, self.padding_left, self.padding_down)

        for pared in self.mapa:
            pared.draw(self.tile_width, self.tile_height, self.padding_left, self.padding_down)

        for aSession in self.peers:
            walter = self.peers[aSession]
            walter.draw(self.tile_width, self.tile_height, self.padding_left, self.padding_down)

    def delete_player(self, session_id):
        del self.peers[session_id]

    def add_player(self, session_id, (x,y), description, is_me):
        image = self.red_walter if is_me else self.walter
        player = Walter((x,y), description, image)
        self.peers[session_id] = player

class Sprite(object):
    def __init__(self, (x,y), image):
        self.x, self.y = x,y
        self.image = image
    def draw(self, tile_width, tile_height, padding_left, padding_down):
        iso_x = (self.y + self.x)*0.91
        iso_y = (self.y - self.x)*0.91
        self.image.blit(tile_width*(iso_x+padding_left), tile_height*(iso_y+padding_down))


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