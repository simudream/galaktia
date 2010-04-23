#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext'

import re

from galaktia.persistence.base import GenericDAO
from galaktia.persistence.orm import SceneObject, Ground, User, Item, \
     CharacterItem, Sprite, Character, Spatial, Wall

class DAOLocator(object):
    """ DAO Service Locator. Has all available DAOs that extend GenericDAO """

    # Example:
    # dao = DAOLocator(session)
    # lennon = dao.character.get('John')
    # bird = dao.character_item.get_by(owner='Paul', ability='sing')
    # stairway = dao.spatial.get_by(z=HEAVEN_ALTITUDE, led='Zeppelin')
    # pink_floyd = dao.wall.filter(we.need != 'education', \
    #       we.need != 'thoughts control')

    _UPPERCASE_PATTERN = re.compile('[A-Z]+')

    def __init__(self, session, **extra_daos):
        """ Sets own members with available DAOs that extend GenericDAO """
        for dao_class in self._locate_subclasses(GenericDAO):
            dao = dao_class(session) # constructor must accept session arg
            setattr(self, self._get_dao_name(dao), dao)
        for name, dao in extra_daos.iteritems():
            setattr(self, name, dao)

    def _locate_subclasses(self, klass):
        """ Recursively locates subclasses for given class """
        for cls in klass.__subclasses__():
            yield cls
            for subcls in self._locate_subclasses(cls):
                yield subcls

    def _get_dao_name(self, dao):
        """ Names DAOs with their entity names in underscore notation """
        name = dao.klass.__name__
        to_underscore = lambda m: '_' + m.group(0).lower()
        return self._UPPERCASE_PATTERN.sub(to_underscore, name).strip('_')

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

    def get_login_info(self, name, passwd):
        return self.get_by(User.name == name, User.passwd == passwd)
            # why not?: user_dao.get(user_id)
            # Ok.


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

    def by_id(self, id):
        return self.get_by(id=id)


class CharacterItemDAO(SpriteDAO):
    ENTITY_CLASS = CharacterItem
