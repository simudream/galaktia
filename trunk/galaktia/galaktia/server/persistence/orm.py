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

# XXX README: latest edits:
# - Replaced String column types by Unicode
# - New SceneObject hierarchy. Tile deprecated
# - Replaced Active by Sprite
# - Replaced Avatar by Character (with foreign key to User, null for NPCs)
# - Deleted redundant nullable=False (primary key implies non-nullable)
# - Etc.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Float, Boolean, DateTime

Entity = declarative_base()

class User(Entity):
    """ Represents a user, with his or her account information """
    __tablename__= 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(26), unique=True, nullable=False)
        # My full name is 26 characters long
            # hahahaha +1!
    passwd = Column(Unicode(42), nullable=False)
        # Long passwords are safe.
    email = Column(Unicode(42), unique=True, nullable=False)
        # id is the binding between a user and his avatars

    def __init__(self, name, email, passwd):
        self.name=name
        self.email=email
        self.passwd=passwd

    def __repr__(self):
        return "<User %s (%i)>" % (self.name, self.id)

# Wouldn't be better if we keep this out of the database, in a special class
# using lists or something?
class Session(Entity):
    """ Represents the client-server session with a user """
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(Unicode(31))
    port = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    character_id = Column(Integer, ForeignKey('characters.id')) # efficiency?
    last_activity = Column(DateTime) # last time session was active

class SceneObject(Entity):
    """ Anything that exists in the world """
    __tablename__ = 'scene_objects'
    id = Column(Integer, primary_key=True) # unique identifier
    type = Column(Unicode(31), index=True) # used for polymorphism
    name = Column(Unicode(127)) # name or description of the object
    x = Column(Integer) # x coord
    y = Column(Integer) # y coord
    z = Column(Integer) # z coord, TODO: decide on how to use layers
    # NOTE: position might be null (e.g.: item owned by character)
    __mapper_args__ = {'polymorphic_on': type} # leave as last class attr
        # TODO: make a double index on x, y:
        # Index('scene_objects_coord_index', SceneObject.x, SceneObject.y)

class Ground(SceneObject):
    """ An object whose sole purpose is to aid the collision system to detect
    boundaries and paths for the walk-able map."""
    __tablename__ = 'ground'
    __mapper_args__ = {'polymorphic_identity': u'ground'}
    id = Column(Integer, ForeignKey('scene_objects.id'), primary_key=True)
    image = Column(Unicode(42))
        # Image identifier, NOT the actual image.
    def __init__(self, x, y, z=0):
        self.x=x
        self.y=y
        self.z=z


class Item(SceneObject):
    """ Represents an item """
    __tablename__ = 'items'
    __mapper_args__ = {'polymorphic_identity': u'item'}
    id = Column(Integer, ForeignKey('scene_objects.id'), primary_key=True)
    cost = Column(Integer) # how much money to pay for buying it
                           # or None if not for sell

class Sprite(SceneObject):
    """ Represents a moving object with some "skin" appearance """
    __tablename__ = 'sprites'
    __mapper_args__ = {'polymorphic_identity': u'sprite'}
    id = Column(Integer, ForeignKey('scene_objects.id'), primary_key=True)
    direction = Column(Integer)
        # direction ranges from 0 to 7, starting North & counting clockwise.
    speed = Column(Integer) # how fast can the sprite move
    arrival_timestamp = Column(DateTime) # time when it reaches current x, y
    skin = Column(Unicode(42)) # an identifier for its appearance
        # 42 is The Answer to the Ultimate Question of Life, the Universe,
        # and Everything, as calculated by an enormous supercomputer over a
        # period of 7.5 million years
    controller = Column(Unicode(127))
        # controller identifies the component that handles actions
        # on interaction events with this sprite

class Character(Sprite):
    """ Represents a character (controlled by a user if user_id not None) """
    __tablename__ = 'characters'
    __mapper_args__ = {'polymorphic_identity': u'character'}
    id = Column(Integer, ForeignKey('sprites.id'), primary_key=True)
    level = Column(Integer, nullable=False) # player "level" (?)
    life = Column(Integer) # life points
    money = Column(Integer) # money points
    user_id = Column(Integer, ForeignKey('users.id')) # binds to User

class Bag(Entity):
    """ Represents ownership of a certain number of items by a character """
    __tablename__ = 'bags'
    character_id = Column(Integer, ForeignKey('characters.id'), \
            primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    count = Column(Integer)

def init_db(db_connection_string='sqlite:///:memory:', echo=False):
    """
    Initializes database model and ORM.

    :parameters:
        db_connection_string : str
            Connection string for database engine

    :returns:
        tuple with database engine, ORM metadata and a session factory
    """
    engine = create_engine(db_connection_string, echo=echo)
    Session = scoped_session(sessionmaker(bind=engine))
        # Session is a factory that reuses the same session instance
        # e.g.: session = Session()
    Entity.metadata.bind = engine
    Entity.metadata.create_all() # TODO: drop/use existing or raise exception?
        # XXX Check whether this works only when all entities were imported
    return (engine, Entity.metadata, Session)

if __name__ == '__main__':
    # Test database schema setup (with echo on)
    init_db(echo=True)

