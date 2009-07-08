#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# Is this necessary? The modules are on the same path... Yes!
from galaktia.server.persistence.base import GenericDAO
from galaktia.server.persistence.orm import SceneObject

class SceneObjectDAO(GenericDAO):
    """
    Data Access Object for SceneObject entities.
    """

    def __init__(self, session):
        super(SceneObjectDAO, self).__init__(session, SceneObject)

    def getLayer(self, layer):
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
        assert x >= 0 and y >= 0 and layer >= 0 # more clear
        # ... but why can't we user negative coords??
        return self.filter(SceneObject.x==x, SceneObject.y==y, \
                SceneObject.z==layer)

    def getLayerSubsection(self, x, y, layer, radius=2):
        """
            Return a square layer subsection. The diameter is twice the
        radius less one. The number of elements is equal to (2*radius-1)^2.
        """
        assert x>=0 and y>=0 and radius>=0 and layer >=0 # more clear
        bigX = x+radius
        smallX = (0 if x-radius < 0 else x-radius)
        bigY = y+radius
        smallY = (0 if y-radius < 0 else y-radius)
        return self.filter(SceneObject.x <= bigX, \
                SceneObject.x >= smallX, SceneObject.y <= bigY, \
                SceneObject.y >= smallY, SceneObject.z == layer)

#class Actives(GenericDao):
#    """
#    Actives is a database abstraction of every Active currently instanciated
#    in-game. This objects are no more than a certain 2D position and Instance,
#    bound to an Avatar, Mob or any other Object.
#    """
# DEPRECATED! We don't want code duplication

# Excellent job! :) :) :)
# Keep subclassing GenericDAO and providing more methods that
# are particularly useful for each Entity class.
# By the way, I recommend writing all DAOs in this file and doing:
# svn mv map.py dao.py
# svn rm userEntities.py

