#!/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

# Documentation on what this module does:
# http://www.sqlalchemy.org/docs/05/reference/ext/declarative.html
# http://www.sqlalchemy.org/docs/05/reference/orm/sessions.html
# http://www.ibm.com/developerworks/aix/library/au-sqlalchemy/
# http://stackoverflow.com/questions/860313/sqlalchemy-is-convoluted/860414

# TODO: Add active session data storage. Message passing should be acomplished
# by using wrapped priority queues.


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

Entity = declarative_base()

class Tile(Entity):
    """ Represents map tiles with x, y coordinates on a z layer """
    __tablename__ = 'tiles'
    x = Column(Integer, primary_key=True, nullable = False)
    y = Column(Integer, primary_key=True, nullable = False)
    z = Column(Integer, primary_key=True, nullable = False)
    id = Column(Integer, nullable = False)

class Sprite(Entity):
    """ Represents a moving object with some "skin" appearance """
    __tablename__ = 'sprites'
    id = Column(Integer, primary_key=True,  nullable = False)
    direction = Column(Integer)
        # direction ranges from 0 to 7, starting North & counting clockwise.
    skin = Column(String(42), nullable = False)
        # 42 is The Answer to the Ultimate Question of Life, the Universe,
        # and Everything, as calculated by an enormous supercomputer over a
        # period of 7.5 million years

class User(Entity):
    """ Represents a User and essential account information"""
    __tablename__= 'users'
    name = Column(String(26), primary_key=True, nullable = False)
        # My full name is 26 characters long
    passwd = Column(String(42), nullable = False)
        # Long passwords are safe.
    email = Column(String(42), nullable = False, key='email')
        # id is the binding between a user and his avatars
    id = Column(Integer, nullable = False)



class Avatar(Entity):
    """
        An avatar is the incarnation of the user In-Game. It binds the User
    to a Sprite and attributes such as Life Points and Items.
    """
    __tablename__= 'avatars'
    id = Column(Integer, primary_key=True, nullable = False)
        # id is the binding between the avatar and the avatar layer
        # it can be used to bind items and other data to a certain avatar.
    name = Column(String(42), primary_key=True, nullable = False)
    level = Column(Integer, nullable = False)

class Active(Entity):
    """
        There are certain objects in the world that are "active", or have their
    own will. Those can be Statics (things like tables, chairs, decoration),
    and Mobiles, such as Mobs and Users. Their location is represented by
    this database abstraction.
    """
    __tablename__= 'actives'
    # Users are *not* tiles, and since it really doesn't matter if they're
    # stacked one over the other, we don't really care about layers. But we
    # *do* care about instances!
    id = Column(Integer, nullable = False)
    x = Column(Integer, nullable = False)
    y = Column(Integer, nullable = False)
    instance = Column(Integer)


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

