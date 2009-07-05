#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tile(Base):
    __tablename__ = "tiles"
    x = Column("x", Integer)
    y = Column("y", Integer)
    layer = Column("z", Integer)
    typeId = Column("id", Integer)


    def __init__(self, x, y, layer, typeId):
        self.x=x
        self.y=y
        self.layer=layer
        self.typeId=typeId


    def __repr__(self):
        return "<Tile object, located in x %i - y %i, layer %i, id i%>" %
        (self.x, self.y, self.z, self.id)

    def asTuple(self):
        return (self.x, self.y, self.z, self.id)


