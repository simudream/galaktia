#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext'

from time import time
from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject, Ground, User, Item, \
     CharacterItem, Sprite, Character, Spatial, Wall
from galaktia.protocol.codec import SerializationCodec


def mass_unpack(list):
    result = []
    for i in list:
        result.append(i.unpack())
    return result


class Resolver(object):

    def resolve(self, class_path):
        path = class_path.split('.')
        class_name = path[-1]
        module_path = '.'.join(path[:-1])
        try:
            return globals()[class_name]
        except KeyError:
            try:
                module = globals()[path[-2:-1]]
            except:
                module = __import__(module_path)
            if class_name not in module.__dict__:
                raise Exception('%s not found in %s.' %
                        (class_name, module_path))
            return getattr(module, class_name)


class DAOResolver(Resolver):
    '''
    Resolves and keeps instances of DAO classes
    '''

    def __init__(self, db_session):
        '''
        Instance DAOResolver

        : parameters :
            db_session : object
                The database session
        '''
        self.db = db_session
        self.user = UserDAO(self.db())
        self.char = CharacterDAO(self.db())
        self.wall = WallDAO(self.db())
        self.spatial = SpatialDAO(self.db())

    # I'm not lazy, but writing all these attributes is nonsense.
    # This is the most reasonable solution.

    def __getattr__(self, name):
        class_name = "%sDAO" % (name.title())
        path = 'galaktia.server.persistence.dao.%s' % class_name
        try:
            Class = self.resolve(path)
            instance = Class(self.db())
            setattr(self, name, instance)
            return instance
        except Exception as e:
            raise AttributeError, e


class SceneObjectDAO(GenericDAO):
    """
    Data Access Object for SceneObject entities.
    """
    ENTITY_CLASS = SceneObject

    def __init__(self, session):
        super(SceneObjectDAO, self).__init__(session, self.ENTITY_CLASS)

    def get_layer(self, layer):
        """Returns a set of SceneObject objects with the selected id"""
        if (layer < 0):
            raise Exception("Layer must be a non-negative integer")
        # assert layer >=0
        return self.filter(self.klass.z == layer)

    def get_by_coords(self, x, y, layer):
        """Returns the SceneObject in x, y, layer"""
        return self.filter(self.klass.x == x, self.klass.y == y, \
                self.klass.z == layer)

    def get_cube_zone(self, (x1, y1, z1), (x2, y2, z2)):
        """
            Returns the objects in the cube zone.
        """
        if z2 == None:
            z2 = z1
        max_x = max(x1, x2)
        min_x = min(x1, x2)
        max_y = max(y1, y2)
        min_y = min(y1, y2)
        max_z = max(z1, z2)
        min_z = min(z1, z2)
        return self.filter(self.klass.x <= max_x, self.klass.x >= min_x, \
                self.klass.y <= max_y, self.klass.y >= min_y, \
                self.klass.z <= max_z, self.klass.z >= min_z)

    def get_layer_subsection(self, x, y, layer, radius=2):
        """
            Returns a square layer subsection. The diameter is twice the
        radius less one. The number of elements is equal to (2*radius-1)^2.
        """
        assert layer >= 0 and radius >= 1
        big_x = x + radius
        small_x = x - radius
        big_y = y + radius
        small_y = y - radius
        return self.filter(self.klass.x <= big_x, \
                self.klass.x >= small_x, self.klass.y <= big_y, \
                self.klass.y >= small_y, self.klass.z == layer)

    def get_near(self, obj, radius=2, return_self=False):
        list = self.get_layer_subsection(obj.x, obj.y, obj.z, radius)
        if not return_self:
            list.remove(obj)
        return list


class SpatialDAO(SceneObjectDAO):
    ENTITY_CLASS = Spatial

    def dismiss(self, obj):
        """
            Dismiss or disconnect a Sprite. This will hide the object from
            being fetched by the move function. Equivalent to
            obj.show = False, obj.collide = False
        """
        obj.show = False
        obj.collide = False

    def materialize(self, obj, collide=False):
        obj.show = True
        obj.collide = collide


class WallDAO(SpatialDAO):
    """ Wall objects are used for collision purposes. They represent
        walls and any other collidable, non-movable objects.
    """
    ENTITY_CLASS = Wall


class GroundDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    ENTITY_CLASS = Ground


class UserDAO(GenericDAO):
    """ Class that provides the basic user management class """

    def __init__(self, session):
        super(UserDAO, self).__init__(session, User)
            # calls superclass constructor with args: session, klass

    def get_user(self, id):
        return self.get(User.id == id)
            # why not?: user_dao.get(user_id)


class ItemDAO(SceneObjectDAO):
    ENTITY_CLASS = Item


class SpriteDAO(SpatialDAO):
    ENTITY_CLASS = Sprite

    def get_los(self, obj, radius=2, return_self=False):
        assert radius > 0
        max_x, min_x = obj.x + radius, obj.x - radius
        max_y, min_y = obj.y + radius, obj.y - radius
        ret = self.filter(self.klass.show == True, self.klass.x <= max_x, \
                self.klass.x >= min_x, self.klass.y <= max_y, self.klass.y >= \
                min_y)
        if not return_self:
            ret.remove(obj)
        return ret


class CharacterDAO(SpriteDAO):
    ENTITY_CLASS = Character

    def get_by_user_id(self, user_id):
        return self.filter(self.klass.user_id == user_id)


class CharacterItemDAO(SpriteDAO):
    ENTITY_CLASS = CharacterItem
