#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# "import *"s ARE BAD
from galaktia.server.persistence.GenericDao import *
from galaktia.server.persistence.Tile import *

# THIS CLASS SHOULD BE A TILE DAO, THAT EXTENDS THE GENERIC DAO
class Map(object):
    """
    The Map class is the representation of the database. It is the only way to
    querry the stored points.
    """

    def __init__(self, session):
        self.layerDao=GenericDao(session, Tile)

    def getLayer(self, layer):
        """Returns a set of Tile objects with the selected id"""
        # TODO: Check for negative numbers and other illegal values.
        return self.dao.filter(Tile.layer==layer)


    def getTile(self, x, y, layer):
        """Returns the Tile in x, y, layer"""
        # TODO: check for illegal values.
        return self.dao.get(Tile.x==x, Tile.y==y, Tile.layer==layer)

    def getLayerSubsection(self, radius=2, x, y, layer):
        """
            Return a square layer subsection. The diameter is twice the
        radius less one. The number of elements is equal to (2*radius-1)^2.
        """
        assert x>=0 and y>=0 and radius>=0 and layer >=0
        bigX = x+radius
        smallX = (0 if x-radius < 0 else x-radius)
        bigY = y+radius
        smallY = (0 if y-radius < 0 else y-radius)
        #return self.dao.filter(Tile.x <= bigX, Tile.x >= smallX, Tile.y <=
        #        bigY, Tile.y >= smallY, )
        # TODO: See the way to filter the results without using nasty tricks. I
        # should modify GenericDAO (base.py)
        return 0
