#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# Is this necessary? The modules are on the same path... Yes!
from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject, Ground, User

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
        return self.filter(SceneObject.z==layer)

    # NOTE: Underscored methods and filenames are more Pythonic.
    #       We prefer to leave CamelCase only for classnames.
    #       See PEP 7 and PEP 8 for more on Python coding style.
    def get_by_coords(self, x, y, layer):
        """Returns the SceneObject in x, y, layer"""
        return self.filter(SceneObject.x==x, SceneObject.y==y, \
                SceneObject.z==layer)

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
        return self.filter(SceneObject.x <= bigX, \
                SceneObject.x >= smallX, SceneObject.y <= bigY, \
                SceneObject.y >= smallY, SceneObject.z == layer)


# I don't know how to subclass SceneObjectDAO and tell the superclass to return
# only Ground objects.
class GroundDAO(SceneObjectDAO):
    """ This class represents the basic world environment, often called as
        'map'. The first (default) layer represents the path where the user can
        walk.
    """
    def __init__(self, session):
        super(GroundDAO, self).__init__(session)


class UserDAO(GenericDAO):
    def __init__(self, session):
        self.klass = User
        self.dao = GenericDAO(session, User)

    # XXX: Ugly bug. Try creating a user and then getting it by this method...
    # You'll find out that you get '(InterfaceError) Error binding parameter 0'
    # PS: use dao.User, otherwise if you use the User class from orm it thinks
    # it is *NOT* the same class. I hate you, classloader.
    def get_user(self, id):
        return self.dao.get(User.id==id)

    def add_user(self, user):
        """ Adds an User to the database """
        if (isinstance(user, User)):
            self.dao.add(user)
        else:
            raise Exception("This is not a User! >:(")

    def delete_user(self, user):
        """ Deletes the User. Behaviour changes according the parameter. If
        user is an int, then it will delete by id; if user is an User object
        then it will delete that object"""
        if (isinstance(user, User)):
            self.dao.delete(user)
        elif (isinstance(user, int)):
            self.dao.delete_by_id(user)
        else:
            raise Exception("This is not a User! >:(")

# Excellent job! :) :) :)
# Keep subclassing GenericDAO and providing more methods that
# are particularly useful for each Entity class.
# By the way, I recommend writing all DAOs in this file.
