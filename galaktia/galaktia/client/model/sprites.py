#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import pyglet.media

from galaktia.client.paths import IMAGES_DIR

class GameView(object):
    def __init__(self, map_dim, grid_size, padding_left, padding_down, surroundings):
        self.grid_size = grid_size
        self.padding_left = padding_left
        self.padding_down = padding_down

        self.walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'walter.gif'))
        self.red_walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'walter2.gif'))
        self.piso = pyglet.image.load(os.path.join(IMAGES_DIR, 'piso.gif'))
        self.pared = pyglet.image.load(os.path.join(IMAGES_DIR, 'pared.gif'))

        self.mapa = [(t[0],t[1]) for t in surroundings]
        self.baldosas = []
        for x in xrange(map_dim):
            for y in xrange(map_dim):
                self.baldosas.append(Baldosa((x,y), self.piso))
        self.peers = {}

    def draw(self):
        for baldosa in self.baldosas:
            baldosa.draw(self.grid_size, self.padding_left, self.padding_down)

        for x,y in self.mapa:
            self.pared.blit(self.grid_size*(x+self.padding_left),self.grid_size*(y+self.padding_down))

        for aSession in self.peers:
            walter = self.peers[aSession]
            walter.draw(self.grid_size, self.padding_left, self.padding_down)

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
    def draw(self, grid_size, padding_left, padding_down):
        self.image.blit(grid_size*(self.x+padding_left), grid_size*(self.y+padding_down))


class Walter(Sprite):

    def __init__(self, (x,y), description, image):
        self.name = description
        super(Walter, self).__init__((x,y), image)

    def set_position(self,x,y):
        self.x, self.y = x, y


class Baldosa(Sprite):
    pass