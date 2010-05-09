# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext'


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
        """ Retrieves first entity that matches criteria given by keywords.

        :keywords:
            attribute key/values
        """
        assert len(kwargs) > 0
        return self._query().filter_by(**kwargs).first()

    def flush(self):
        self.session.flush()

    def get(self, *args, **kwargs):
        """ Returns an entity by primary key """
        assert len(args) > 0 or len(kwargs) > 0
        return self._query().get(*args, **kwargs)

    def new(self, **kwargs):
        obj = self.klass()
        for k, v in kwargs.iteritems():
            setattr(obj, k, v)
        self.session.add(obj)
        return obj

    def filter(self, *args, **kwargs):
        """ Returns all entities matching the filters criteria """
        # params are inequalities.
        # assert len(args) > 0 or len(kwargs) > 0
        q = reduce(lambda q, f: q.filter(f), args, self._query())
        q = q.filter_by(**kwargs) if kwargs else q
        return q.all()

    def count(self, **filters):
        """ Counts the number of entities mathing the filters criteria """
        return self._query().filter_by(**filters).count()

    def all(self):
        """ Returns all entities """
        return self._query().all()

    # def save(self, entity): ...
    #     Deprecated in SQLAlchemy 0.5; use add instead

    def add(self, entity):
        """ Adds an entity to the session """
        assert isinstance(entity, self.klass)
        self.session.add(entity)

    def delete(self, entity):
        """ Deletes the given entity """
        assert isinstance(entity, self.klass)
        self.session.delete(entity)

    def delete_by_id(self, entity_id):
        """ Deletes an entity by primary key """
        entity = self.get(entity_id)
        self.delete(entity)

    def expunge(self, entity):
        """ Removes an entity from the session """
        assert isinstance(entity, self.klass)
        self.session.expunge(entity)

    def merge(self, entity):
        """ Reconciles current state of an entity with existing data """
        return self.session.merge(entity)

    def expire(self, entity):
        """ Marks entity attributes as out of date
            (for retrieval on next access) """
        assert isinstance(entity, self.klass)
        self.session.expire(entity)
