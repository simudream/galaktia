# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

class GenericDAO(object):
    """
    A generic Data Access Object for any SQLAlchemy entity.
    """

    def __init__(self, session, klass):
        """ GenericDAO constructor """
        # DANGER! Programmers who access session will die
        self.session = session
        self.klass = klass # class is aktually a reserved qeyword

    def _query(self):
        """ Returns an SQLAlchemy query object for corresponding entity """
        return self.session.query(self.klass)

    def get_by(self, **kwargs):
        """ Returns the first entity that matches kwargs criteria """
        assert len(kwargs) > 0
        return self._query().filter_by(**kwargs).first()

    def get(self, *args, **kwargs):
        """ Returns an entity by primary key """
        assert len(args) > 0 or len(kwargs) > 0
        return self._query().get(*args, **kwargs)

    def filter(self, **filters):
        """ Returns all entities matching the filters criteria """
        assert len(filters) > 0
        return self._query().filter_by(**filters).all()

    def count(self, **filters):
        """ Counts the number of entities mathing the filters criteria """
        return self._query().filter_by(**filters).count()

    def all(self):
        """ Returns all entities """
        return self._query().all()

    def save(self, entity):
        """ Saves a transient (unsaved) entity to the session """
        assert isinstance(entity, self.klass)
        self.session.save(entity)

    def add(self, entity):
        """ Adds an entity to the session """
        assert isinstance(entity, self.klass)
        self.session.add(entity)

    def expunge(self, entity):
        """ Removes an entity from the session """
        assert isinstance(entity, self.klass)
        self.session.expunge(entity)

    def delete(self, entity):
        """ Deletes the given entity """
        assert isinstance(entity, self.klass)
        self.session.delete(entity)

    def delete_by_id(self, entity_id):
        """ Deletes an entity by primary key """
        entity = self.get(entity_id)
        self.delete(entity)

    def expire(self, entity):
        """ Marks entity attributes as out of date
            (for retrieval on next access) """
        assert isinstance(entity, self.klass)
        self.session.expire(entity)

