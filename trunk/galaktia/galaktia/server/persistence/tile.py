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
