#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

class Map(object):
    """
    The Map class is the representation of the database. It is the only way to
    querry the stored points.
    """

    def __init__(self, session):
        self.session=session

    def getLayer(self, id):
        """Returns a list of Tile objects with the selected id"""
        pass

pass

