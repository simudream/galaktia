#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject, Ground, User, Item, \
     Sprite, Character, Spatial, Stationary

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
        
    def get_near(self, obj, radius=2):
        return self.get_layer_subsection(obj.x, obj.y, obj.z, radius)

class SpatialDAO(SceneObjectDAO):
    ENTITY_CLASS=Spatial

    def move(self, obj, x, y):
        result = True
        # Verify that moving from current xy is physically possible, i.e.,
        # it's near.
        # assert (abs(x - obj.x) <= 1) and (abs(y - obj.y) <= 1)
        if(obj.x==x and obj.y==y):
            return True
            # If you want to move to the same place you're in, then return
            # true
        if(abs(x-obj.x)>1) or (abs(y-obj.y)>1):
            return False
        elements = self.get_by_coords(x,y,obj.z)
        if(not elements):
            obj.x=x
            obj.y=y
        else:
            result = False
        return result

class StationaryDAO(SpatialDAO):
    ENTITY_CLASS=Stationary
    def move(self):
        pass

class GroundDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    ENTITY_CLASS=Ground

class UserDAO(GenericDAO):
    def __init__(self, session):
        super(UserDAO, self).__init__(session, User)
            # calls superclass constructor with args: session, klass

    def get_user(self, id):
        return self.get(User.id==id)
            # why not?: user_dao.get(user_id)

    def delete_user(self, user):
        """ Deletes the User. Behaviour changes according the parameter. If
        user is an int, then it will delete by id; if user is an User object
        then it will delete that object"""
        if (isinstance(user, User)):
            self.delete(user)
        elif (isinstance(user, int)):
            self.delete_by_id(user)
        else:
            raise Exception("This is not a User! >:(")
                # why not?: user_dao.delete(user)
                #           user_dao.delete_by(user_id)

class ItemDAO(SceneObjectDAO):
    ENTITY_CLASS=Item


class SpriteDAO(SpatialDAO):
    ENTITY_CLASS=Sprite


class CharacterDAO(SpriteDAO):
    ENTITY_CLASS=Character

