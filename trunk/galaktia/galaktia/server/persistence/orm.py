#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# Documentation on what this module does:
# http://www.sqlalchemy.org/docs/05/reference/ext/declarative.html
# http://www.sqlalchemy.org/docs/05/reference/orm/sessions.html
# http://www.ibm.com/developerworks/aix/library/au-sqlalchemy/
# http://stackoverflow.com/questions/860313/sqlalchemy-is-convoluted/860414

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

Entity = declarative_base()

class Tile(Entity):
    """ Represents map tiles with x, y coordinates on a z layer """
    __tablename__ = 'tiles'
    x = Column(Integer, primary_key=True)
    y = Column(Integer, primary_key=True)
    z = Column(Integer, primary_key=True)
    id = Column(Integer)

class Sprite(Entity):
    """ Represents a moving object with some "skin" appearance """
    __tablename__ = 'sprites'
    id = Column(Integer, primary_key=True)
    direction = Column(Integer)
        # direction ranges from 0 to 7, starting North and counting clockwise.
    skin = Column(String(42))
        # 42 is The Answer to the Ultimate Question of Life, the Universe,
        # and Everything, as calculated by an enormous supercomputer over a
        # period of 7.5 million years

def init_db(db_connection_string='sqlite:///:memory:'):
    """
    Initializes database model and ORM.

    :parameters:
        db_connection_string : str
            Connection string for database engine

    :returns:
        tuple with database engine, ORM metadata and a session factory
    """
    engine = create_engine(db_connection_string, echo=True)
    Session = scoped_session(sessionmaker(bind=engine))
        # Session is a factory that reuses the same session instance
    Entity.metadata.create_all()
        # XXX Check whether this works only when all entities were imported
    return (engine, Entity.metadata, Session)

