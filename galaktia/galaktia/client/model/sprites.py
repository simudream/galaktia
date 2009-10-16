#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import pyglet.media
from pyglet.gl import glEnable,GL_BLEND,glBlendFunc,GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA

from galaktia.client.paths import IMAGES_DIR

class GameView(object):
    def __init__(self, (screen_width, screen_height), map_dim, (tile_width, tile_height), padding_left, padding_down, surroundings):
        self.miWalter = Walter3D(pyglet.image.load(os.path.join(IMAGES_DIR, 'humano.png')), screen_width, screen_height)
        
        self.tile_size = {'x':tile_width, 'y':tile_height}
        self.padding = {'x':padding_left, 'y':padding_down}

        self.walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'walter.png'))
        self.red_walter = pyglet.image.load(os.path.join(IMAGES_DIR, 'red_walter.png'))
        self.piso = pyglet.image.load(os.path.join(IMAGES_DIR, 'piso.png'))
        self.pared = pyglet.image.load(os.path.join(IMAGES_DIR, 'pared.png'))
        
        self.mapa = [Pared((t[0],t[1]), 'Pared', self.pared, self.tile_size, self.padding) \
                     for t in surroundings]
        self.baldosas = []
        for x in xrange(map_dim):
            for y in xrange(map_dim):
                self.baldosas.append(Baldosa((x,y), 'Baldosa', self.piso, self.tile_size, self.padding))
        self.peers = {}
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.center_walter = {'x':0, 'y':0}
        self.own_walter = None

    def draw(self):
        if self.own_walter is not None:
            self.center_walter = {'x': self.own_walter.x, 'y': self.own_walter.y}
        else:
            self.center_walter = {'x': 0, 'y': 0}
        for baldosa in self.baldosas:
            baldosa.draw(self.center_walter)
        for pared in self.mapa:
            pared.draw(self.center_walter)
        for aSession in self.peers:
            self.peers[aSession].draw(self.center_walter)
        self.miWalter.draw()

    def delete_player(self, session_id):
        del self.peers[session_id]

    def add_player(self, session_id, (x,y), description, is_me):
        image = self.red_walter if is_me else self.walter
        player = Walter((x,y), description, image, self.tile_size, self.padding)
        self.peers[session_id] = player
        if is_me:
            self.center_walter['x'] = x
            self.center_walter['y'] = y
            self.own_walter = player
        #if is_me:
            ##TODO: make each walter a 3DWalter
            #self.miWalter.x = x
            #self.miWalter.y = y
            #self.own_walter = self.miWalter
            #return
        #player = Walter((x,y), description, self.walter, self.tile_size, self.padding)
        #self.peers[session_id] = player


class Sprite(object):
    def __init__(self, (x,y), description, image, tile_size, padding):
        self.sprite = pyglet.sprite.Sprite(img=image, x=0, y=0)
        self.x, self.y = x,y
        self.description = description
        self.tile_size = tile_size
        self.padding = padding

    def draw(self, center):
        iso_x = (self.y - center['y'] + self.x - center['x'])*0.91
        iso_y = (self.y - center['y'] - self.x + center['x'])*0.91

        self.sprite.x = self.tile_size['x']*iso_x+self.padding['x']
        self.sprite.y = self.tile_size['y']*iso_y+self.padding['y']
        self.sprite.draw()

    def set_screen_options(self, tile_size, padding):
        self.tile_size = tile_size
        self.padding = padding


class Walter(Sprite):

    def __init__(self, (x,y), description, image, tile_size, padding):
        self.name = description
        super(Walter, self).__init__((x,y), description, image, tile_size, padding)

    def set_position(self,x,y):
        self.x, self.y = x, y

    def set_facing(self, direction):
        pass

class Walter3D(dict):
    """Class Walter.
    
    Controls, Shows and Represents a character in the game.
    """
    def __init__(self, image, screen_width, screen_height):
        """Initializer.
        
        Takes an image, which has to be an array of images with:
        size of the array: 8 rows (one for each orientation), 15 columns.
        size of each frame: 50 pixels width, 100 pixels height
        
        In each row, the first image is the still position, and the other 14
        images are the animation for walking.
        
        TODO: Open several images, one for each action that the player can do
        (examples: combat position, attacking position, bow, using a device)
        """
        # redefine some big names
        panimation = pyglet.image.Animation
        paframe = pyglet.image.AnimationFrame
        psprite = pyglet.sprite.Sprite
        assert (image.width, image.height) == (750,800), \
            'Image size must be 750x800'
        
        # Now we create two dicts, one for the moving character and one for the
        # character when he's standing still. The former is an animation
        # sprite. These dicts map numbers from 0 to 7 to a sprite.
        middle_x, middle_y = screen_width/2-12, screen_height/2

        self['moving'] = dict([(a, psprite(img=panimation( # 0.03 seconds/frame
            [paframe(image.get_region(b*50, 700-a*100, 50, 100), 0.06)
            for b in range(1, 15)]), x=middle_x, y=middle_y))
            for a in range(8)])
        self['still'] = dict([
             (a, psprite(img=image.get_region(0, 700-a*100, 50, 100),
             x=middle_x, y=middle_y)) for a in range(8)])
        
        self.state = 'still'
        self.orientation = 4
    
    def set_orientation(self, direction):
        """Method set_orientation
        
        Sets Walter's orientation based on a clock-wise direction.
        North is set to 0:
        
                0
             7     1
          6     X     2
             5     3
                4
        """
        self.orientation = direction
    
    def draw(self):
        """Draws the current state in the screen"""
        sprite = self[self.state][self.orientation]
        sprite.draw()
    
    def start_moving(self):
        self.state = 'moving'
    
    def stop_moving(self):
        self.state = 'still'

class Baldosa(Sprite):
    pass
class Pared(Sprite):
    pass
