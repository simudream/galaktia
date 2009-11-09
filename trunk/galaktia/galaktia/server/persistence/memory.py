#/usr/bin/env python

"""
Memory decorator and utilites to speed up access to computationally expensive
functions.
"""

from threading import Lock
from functools import wraps
from memcache import Client as MemcacheClient
import logging
try:
    from cPickle import dumps
except ImportError:
    from pickle import dumps

class Null():
    pass

class Memory(object):
    """
        Memory objects are key-value gateways to a database or any other kind of
       memory storage. They behave the same way dictionaries do, which makes it
       easier to mock them.

        Required methods are __getitem__, __setitem__ and __delitem__.
    """

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

class MemcacheMemory(Memory):
    """
        Memory gateway to a Memcache server
    """

    def __init__(self, servers=["127.0.0.1:11211"], expire=300):
        """
            :param servers: List of servers to use. Please, read
            memcache.Client help.

        """
        self._client = MemcacheClient(servers)
        self._expire = expire

    def __getitem__(self, key):
        value = self._client.get(key)
        if value is Null:
            return None
        elif value is None:
            raise KeyError
        else:
            return value

    def __setitem__(self, key, value):
        if value is None:
            value = Null()
        self._client.set(key, value)

    def __delitem__(self, key):
        if self._client.delete(key) == 0:
            raise KeyError

class MemoryPool(Memory):
    """
        A MemoryPool object provides an extended way of using Memory gateways.
        It holds more than one connection open, so it should be theoretically
        faster than ad-hoc connections.

        It *must* behave like a Memory gateway too.
    """
    def count(self):
        raise NotImplementedError

    def grow(self, number=1):
        raise NotImplementedError

    def reduce(self, number=1):
        raise NotImplementedError


class Memorized(object):
    def __init__(self, f, memo):
        self.__f = f
        self.__memo = memo

    def __create_key(self, f, *args, **kwargs):
        return "f-%s %s %s" % (f.__name__, repr(args), repr(kwargs))
#        return dumps((f.__name__, args, kwargs))

    def __call__(self, *args, **kwargs):
        key = self.__create_key(self.__f, args, kwargs)
        try:
            return self.__memo[key]
        except KeyError:
            val = self.__f(*args, **kwargs)
            self.__memo[key] = val
            return val


class memorize(object):
    def __init__(self, memory):
        self._memory = memory

    def __call__(self, f):
        memo = Memorized(f, self._memory)
        wraps(f)(memo)
        return memo


if __name__ == "__main__":
    memory = MemcacheMemory()
    @memorize(memory)
    def test(a):
        """test test test!!!"""
        if a > 1:
            return a*test(a-1)
        elif a == 1:
            return 1;
        else:
            return None

    print test.__name__
    print test.__class__
    print test.__doc__
    print test(4)
    print test(6)
    print test(-1)
