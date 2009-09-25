#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from time import time

from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject, Ground, User, Item, \
     CharacterItem, Sprite, Character, Spatial, Stationary
from galaktia.protocol.codec import SerializationCodec

def mass_unpack(list):
    result = []
    for i in list:
        result.append(i.unpack())
    return result

class SceneObjectDAO(GenericDAO):
    """
    Data Access Object for SceneObject entities.
    """
    ENTITY_CLASS=SceneObject

    def __init__(self, session):
        super(SceneObjectDAO, self).__init__(session, self.ENTITY_CLASS)

    def get_layer(self, layer):
        """Returns a set of SceneObject objects with the selected id"""
        if (layer < 0):
            raise Exception("Layer must be a non-negative integer")
        # assert layer >=0
        return self.filter(self.klass.z==layer)

    # NOTE: Underscored methods and filenames are more Pythonic.
    #       We prefer to leave CamelCase only for classnames.
    #       See PEP 7 and PEP 8 for more on Python coding style.
    def get_by_coords(self, x, y, layer):
        """Returns the SceneObject in x, y, layer"""
        return self.filter(self.klass.x==x, self.klass.y==y, \
                self.klass.z==layer)

    def get_layer_subsection(self, x, y, layer, radius=2):
        """
            Returns a square layer subsection. The diameter is twice the
        radius less one. The number of elements is equal to (2*radius-1)^2.
        """
        assert layer >= 0 and radius >=1
        bigX = x+radius
        smallX = x-radius
        bigY = y+radius
        smallY = y-radius
        return self.filter(self.klass.x <= bigX, \
                self.klass.x >= smallX, self.klass.y <= bigY, \
                self.klass.y >= smallY, self.klass.z == layer)
    
    def get_near(self, obj, radius=2, return_self=False):
        list = self.get_layer_subsection(obj.x, obj.y, obj.z, radius)
        if not return_self:
            list.remove(obj)
        return list
    

class SpatialDAO(SceneObjectDAO):
    ENTITY_CLASS=Spatial
    
    def move(self, obj, x, y, z=None, collide_objects=True, warp=False):
        # Verify that moving from current xy is physically possible, i.e.,
        # it's near.
        result=True
        if(z is None):
            z=obj.z
        if(obj.x==x and obj.y==y and obj.z==z):
            return True
            # If you want to move to the same place you're in, then return
            # true
        if not warp and ((abs(x-obj.x)>1) or (abs(y-obj.y)>1) or \
                (abs(z-obj.z)>1)):
            return False
        # XXX: DO NOT CHANGE. When you inherit this class you will overwrite
        # ENTITY_CLASS, returning *only* the heir's objects, NOT Spatials.
        # This hack prevents you from breaking the correct behaviour of the
        # method after being inherited.
        sdao = StationaryDAO(self.session)
        stationaries = sdao.get_by_coords(x, y, z)
        if(collide_objects and (isinstance(obj,self.klass) or \
                (hasattr(obj, "show") and hasattr(obj, "collide"))) and \
                obj.collide==True):
            # If the flag is enabled and is a Spatial-like entity, and if you
            # can collide (i.e.: not a "ghost")...
            class_objects = self.filter(self.klass.x==x, self.klass.y==y, \
                    self.klass.z==z, self.klass.show==True, \
                    self.klass.collide==True)
            for i in class_objects:
                stationaries.append(i)
        if(not stationaries):
            obj.x=x
            obj.y=y
            obj.z=z
        else:
            result = False
        return result
    
    def dismiss(self, obj):
        """
            Dismiss or disconnect a Sprite. This will hide the object from
            being fetched by the move function. Equivalent to obj.show=False,
            obj.collide=False
        """
        obj.show=False
        obj.collide=False

    def materialize(self, obj, collide=False):
    	obj.show=True
    	obj.collide=collide

class StationaryDAO(SpatialDAO):
    """ Stationary objects are used for collision purposes. They represent
        walls and any other collidable, non-movable objects.
    """
    ENTITY_CLASS=Stationary
    def move(self, obj, x, y):
        """ Since moving Stationary objects is NOT allowed by usual means, you
        should not use this function. It will always return False.
        """
        return False



class GroundDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    ENTITY_CLASS=Ground

class UserDAO(GenericDAO):
    """ Class that provides the basic user management class """
    def __init__(self, session):
        super(UserDAO, self).__init__(session, User)
            # calls superclass constructor with args: session, klass

    def get_user(self, id):
        return self.get(User.id==id)
            # why not?: user_dao.get(user_id)

class ItemDAO(SceneObjectDAO):
    ENTITY_CLASS=Item


class SpriteDAO(SpatialDAO):
    ENTITY_CLASS=Sprite


class CharacterDAO(SpriteDAO):
    ENTITY_CLASS=Character

    def get_by_user_id(self, user_id):
        return self.filter(self.klass.user_id==user_id)


class CharacterItemDAO(SpriteDAO):
    ENTITY_CLASS=CharacterItem

