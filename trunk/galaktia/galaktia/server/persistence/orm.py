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

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relation, backref
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Float, Boolean, DateTime, \
     UnicodeText

Entity = declarative_base()

class User(Entity):
    """ Represents a user, with his or her account information """
    __tablename__= 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(127), unique=True, nullable=False)
    passwd = Column(Unicode(127), nullable=False)
    email = Column(Unicode(127), unique=True, nullable=False)
    
    character = relation('Character', backref='User', uselist=False)
        # id is the binding between a user and his avatars

class SceneObject(Entity):
    """ Anything that exists in the world """
    __tablename__ = 'scene_objects'
    id = Column(Integer, primary_key=True) # unique identifier
    type = Column(Unicode(31), index=True) # used for polymorphism
    name = Column(Unicode(127)) # name or description of the object
    x = Column(Integer) # x coord
    y = Column(Integer) # y coord
    z = Column(Integer) # z coord, TODO: decide on how to use layers
    image = Column(Unicode(42), default=None)
    # NOTE: position might be null (e.g.: item owned by character)
    # NOTE2: We won't support dropping items.
    __mapper_args__ = {'polymorphic_on': type} # leave as last class attr
        # TODO: make a double index on x, y:
        # Index('scene_objects_coord_index', SceneObject.x, SceneObject.y)

    @property
    def pos(self): # suggestion: @property
        return (self.x, self.y, self.z)

    def unpack(self):
        return (self.x, self.y, self.z, self.image)

    def to_dict(self): # useful for serializing
        return dict((k, getattr(self, k)) for k, v in \
                self.__class__.__dict__.iteritems() if \
                isinstance(v, InstrumentedAttribute))

    @classmethod
    def from_dict(cls, d): # useful for deserializing
        entity = cls() # instantiate by calling "this" class
        for k, v in d.iteritems():
            setattr(entity, k, v)
        return entity

class Spatial(SceneObject):
    """ Represents any object with volume in the world. """
    __tablename__ = 'spatials'
    __mapper_args__ = {'polymorphic_identity': u'spatial'}
    id = Column(Integer, ForeignKey('scene_objects.id'), primary_key=True)
    show = Column(Boolean, default=True)
        # Show determines if the object will be shown on screen, or considered
        # disconnected.
    collide = Column(Boolean, default=False)

class Wall(Spatial):
    """ Objects that you can't move. (i.e.: a wall) """
    __tablename__ = 'stationaries'
    __mapper_args__ = {'polymorphic_identity': u'stationary'}
    id = Column(Integer, ForeignKey('spatials.id'), primary_key=True)


class Ground(SceneObject):
    """ The basic map information for the client. """
    __tablename__ = 'ground'
    __mapper_args__ = {'polymorphic_identity': u'ground'}
    id = Column(Integer, ForeignKey('scene_objects.id'), primary_key=True)

class Item(Entity):
    """ Represents the class of an item """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    level = Column(Integer)
    attrs = Column(Unicode(127)) # We can use a pickled dict to hold the data

class ItemType(Entity):
    """ Represents the class of an item (i.e.: gun, armor) """
    __tablename__ = 'item_types'
    id = Column(Integer, primary_key=True)
    type = Column(Unicode(42))

class Sprite(Spatial):
    """ Represents a moving object with some "skin" appearance """
    __tablename__ = 'sprites'
    __mapper_args__ = {'polymorphic_identity': u'sprite'}
    id = Column(Integer, ForeignKey('spatials.id'), primary_key=True)
    direction = Column(Integer)
        # direction ranges from 0 to 7, starting North & counting clockwise.
    speed = Column(Integer) # how fast can the sprite move
    arrival_timestamp = Column(Integer, default=0) # time when it reached current x, y
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
    level = Column(Integer, nullable=False, default=1) # player "level" (?)
    life = Column(Integer) # life points
    money = Column(Integer) # money points
    user_id = Column(Integer, ForeignKey('users.id')) # binds to User


class CharacterItem(Sprite):
    """ Represents ownership of a certain number of items by a character """
    __tablename__ = 'character_items'
    __mapper_args___ = {'polymorphic_identity': u'drop'}
    id = Column(Integer, ForeignKey('sprites.id'), primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))
    item_class = Column(Integer, ForeignKey('items.id'))
    # NOTE: Use description for personalized attributes.
    bag = Column(Integer)
        # 0 for "bank" bag, 1 for "user" bag.
    cost = Column(Integer) # how much money to pay for buying it
                           # or None if not for sell

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
        # WARNING: Only tables for imported Entities are created
    return (engine, Entity.metadata, Session)

if __name__ == '__main__':
    # Test database schema setup (with echo on)
    init_db(echo=True)

