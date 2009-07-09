#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject, Ground, User, Item, \
     Sprite, Character 

class SceneObjectDAO(GenericDAO):
    """
    Data Access Object for SceneObject entities.
    """

    def __init__(self, session):
        super(SceneObjectDAO, self).__init__(session, SceneObject)

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
        

class SpatialDAO(SceneObjectDAO):
    def __init__(self, session):
        super(SpatialDAO, self).__init__(session, Spacia)

    def move(self, obj, x, y):
        result = True
        #verificar que el xy destino sea adyacente al xy del sceneobject.
        #Pedir todos los sceneobjects que están en el xy del type sprite
        #o de type stationary

        # Verify that moving from current xy is physically possible, i.e., 
        # it's near.
        assert (abs(x - obj.x) <= 1) and (abs(y - obj.y) <= 1)
        elements = self.get_by_coords(x,y,obj.z)
        if(not elements):
            obj.x=x
            obj.y=y
        else:
            resut=False
        return result


class GroundDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    def __init__(self, session):
        super(GroundDAO, self).__init__(session, Ground)
            # calls superclass constructor with args: session, klass


class UserDAO(GenericDAO):
    def __init__(self, session):
        super(UserDAO, self).__init__(session, User)
            # calls superclass constructor with args: session, klass

    # XXX: Ugly bug. Try creating a user and then getting it by this method...
    # You'll find out that you get '(InterfaceError) Error binding parameter 0'
    # PS: use dao.User, otherwise if you use the User class from orm it thinks
    # it is *NOT* the same class. I hate you, classloader.
        # This is due to User.__init__, that should not be overriden
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
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    def __init__(self, session):
        super(ItemDAO, self).__init__(session, Item)
            # calls superclass constructor with args: session, klass


class SpriteDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    def __init__(self, session):
        super(SpriteDAO, self).__init__(session, Sprite)
            # calls superclass constructor with args: session, klass


class CharacterDAO(SpriteDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    def __init__(self, session):
        super(CharacterDAO, self).__init__(session, Character)
            # calls superclass constructor with args: session, klass
# Keep subclassing GenericDAO and providing more methods that
# are particularly useful for each Entity class.
# By the way, I recommend writing all DAOs in this file.
