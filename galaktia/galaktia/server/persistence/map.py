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

    def getLayerSubsection(self, radius=2, x, y, layer):
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
                bigY, Tile.y >= smallY, )


