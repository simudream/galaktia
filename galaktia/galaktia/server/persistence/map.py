#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# "import *"s ARE BAD
# Is this necessary? The modules are on the same path...
import galaktia.server.persistence.GenericDao as GenericDao
import galaktia.server.persistence.Tile as Tile

class Map(GenericDAO):
    """
    The Map class is the representation of the database. It is the only way to
    querry the stored points.
    """

    def __init__(self, session):
        self.dao=GenericDao(session, Tile)

    def getLayer(self, layer):
        """Returns a set of Tile objects with the selected id"""
        if (layer < 0):
            raise Exception("Layer must be a non-negative integer")
        # assert layer >=0
        return self.dao.filter(Tile.layer==layer)

    def getTile(self, x, y, layer):
        """Returns the Tile in x, y, layer"""
        if (x < 0):
            raise Exception("X must be a non-negative integer")
        if (y < 0):
            raise Exception("Y must be a non-negative integer")
        if (layer < 0):
            raise Exception("Layer must be a non-negative integer")
        # assert x >= 0 and y >= 0 and layer >= 0
        return self.dao.get(Tile.x==x, Tile.y==y, Tile.layer==layer)

    def getLayerSubsection(self, x, y, layer, radius=2):
        """
            Return a square layer subsection. The diameter is twice the
        radius less one. The number of elements is equal to (2*radius-1)^2.
        """
        if (x < 0):
            raise Exception("X must be a non-negative integer")
        if (y < 0):
            raise Exception("Y must be a non-negative integer")
        if (layer < 0):
            raise Exception("Layer must be a non-negative integer")
        if (radius < 1):
            raise Exception("Radius must be a positive integer")
        # assert x>=0 and y>=0 and radius>=0 and layer >=0
        bigX = x+radius
        smallX = (0 if x-radius < 0 else x-radius)
        bigY = y+radius
        smallY = (0 if y-radius < 0 else y-radius)
        return self.dao.advFilter(Tile.x <= bigX, Tile.x >= smallX, Tile.y <=
                bigY, Tile.y >= smallY, Tile.layer == layer)


class Actives(GenericDao):
    """
    Actives is a database abstraction of every Active currently instanciated
    in-game. This objects are no more than a certain 2D position and Instance,
    bound to an Avatar, Mob or any other Object.
    """

    def __init__(self, session):
        self.dao = GenericDao(session, Active)

    def getActive(self, id):
        """ Returns the only Active by id """
        if (id < 0):
            raise Exception("Invalid ID (must be a non-negative integer)")
        return self.dao.filter(Active.id==id)

    def getInstance(self, instance=0):
        """ Returns all the objects present in the instance """
        if (instance < 0):
            raise Exception("Instance id must be a non-negative integer")
        return self.dao.filter(Active.instance==instance)

    def getInstanceTile(self, x, y, instance=0):
        """ Returns all the Actives in a tile """
        if (instance < 0):
            raise Exception("Instance must be a non-negative integer")
        if (x < 0):
            raise Exception("X must be a non-negative integer")
        if (y < 0):
            raise Exception("Y must be a non-negative integer")
        return self.dao.filter(Active.x=x, Active.y=y,
                Active.instance=instance)

    def getInstanceSubsection(self, x, y, instance=0, radius=2):
        """
           Return a square instance subsection containing all the Active
           objects (Mobs, Statics or Avatars).
        """
        if (x < 0):
            raise Exception("X must be a non-negative integer")
        if (y < 0):
            raise Exception("Y must be a non-negative integer")
        if (instance < 0):
            raise Exception("Instance must be a non-negative integer")
        if (radius < 1):
            raise Exception("Radius must be a positive integer")
        bigX = x+radius
        smallX = (0 if x-radius < 0 else x-radius)
        bigY = y+radius
        smallY = (0 if y-radius < 0 else y-radius)
        return self.dao.advFilter(Active.x <= bigX, Active.x >= smallX,
                Active.y <= bigY, Active.y >= smallY, Active.instance ==
                instance)

