#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

class Tile(object):
    """
    The tile class provides a representation of each tuple stored in the
    database.
    """

    def __init__(self, x, y, z, id):
        self.x=x
        self.y=y
        self.z=z
        self.id=id


    def __repr__(self):
        return "<Tile object, located in x %i - y %i, layer %i, id i%>" %
        (self.x, self.y, self.z, self.id)

    def asTuple(self):
        return (self.x, self.y, self.z, self.id)

