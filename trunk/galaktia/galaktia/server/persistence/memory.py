#/usr/bin/env python

"""
Memory decorator and utilites to speed up access to computationally expensive
functions.
"""

from threading import Lock
from functools import wraps
from memcache import Client as MemcacheClient
from redis import Redis as RedisClient
import logging
from hashlib import md5
try:
    from cPickle import dumps
except ImportError:
    from pickle import dumps


#
#   AUXILIARY CLASSES
#
class NotSet(object):
    """ Empty class used to differenciate None from unsetted values in k-v
        storages that return None in both cases, like python-memcached.
    """
    pass

#
#   PSEUDO-INTERFACES
#

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


#
#   DECORATORS AND FACTORIES
#

class Memorized(object):
    def __init__(self, f, memo, DEBUG=False):
        self.__f = f
        self.__memo = memo
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memorized Callable %s" % f.__name__)
        if DEBUG:
            self.log.setLevel(logging.DEBUG)

    def __create_key(self, f, *args, **kwargs):
#       TODO: Is there another way to create a key?
        the_hash = md5(f.__name__)
        for arg in args:
            the_hash.update(str(arg))
        the_hash.update("|")
        for key, val in kwargs.iteritems():
            the_hash.update("%s:%s;"(i, j))
        return the_hash.hexdigest()

    def __call__(self, *args, **kwargs):
        key = self.__create_key(self.__f, args, kwargs)
        self.log.debug("Calling memorized value %s", key)
        try:
            return self.__memo[key]
        except KeyError:
            self.log.debug("No key %s found. Calculating value...", key)
            val = self.__f(*args, **kwargs)
            self.__memo[key] = val
            return val


class memorize(object):
    def __init__(self, memory):
        self._memory = memory

    def __call__(self, f):
        memo = Memorized(f, self._memory, DEBUG=True)
        wraps(f)(memo)
        return memo


#
#   CONCRETE STORAGES
#

class MemcacheMemory(Memory):
    """
        Memory gateway to a Memcache server
    """

    def __init__(self, servers=["127.0.0.1:11211"], expire=None, DEBUG=False):
        """
            :param servers: List of servers to use. Please, read
            memcache.Client help.

        """
        self._client = MemcacheClient(servers)
        self._expire = expire
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memcache-Gateway")
        if DEBUG:
            self.log.setLevel(logging.DEBUG)

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        value = self._client.get(key)
        if isinstance(value, NotSet):
            return None
        elif value is None:
            raise KeyError
        else:
            return value

    def __setitem__(self, key, value):
        self.log.debug("Setting key")
        if value is None:
            value = NotSet()
        self._client.set(key, value)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        if self._client.delete(key) == 0:
            raise KeyError
            
            
class MemcacheMemoryPool(MemoryPool):
    pass


class RedisMemory(Memory):
    """
        Memory gateway to a Redis server
    """

    def __init__(self, host=None, port=None, expire=None, DEBUG=False, *args, **kwargs):
        """
            :param servers: List of servers to use. Please, read
            redis.Redis help.

        """
        self._client = RedisClient(host=host, port=port, *args, **kwargs)
        self._host = host
        self._port = port
        self._expire = expire
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Redis-Gateway")
        if DEBUG:
            self.log.setLevel(logging.DEBUG)

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        value = self._client.get(key)
        if isinstance(value, NotSet):
            return None
        elif value is None:
            raise KeyError
        else:
            return value

    def __setitem__(self, key, value):
        self.log.debug("Setting key")
        if value is None:
            value = NotSet()
        self._client.set(key, value)
        if self._expire:
            self._client.expire(key, self._expire)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        if self._client.delete(key) == 0:
            raise KeyError
        
    def expire(self, key, time):
        self.log.debug("Setting expire time to %s seconds for key %s", time, key)
        self._client.expire(key, time)



#
#   Tests?
#


if __name__ == "__main__":
    memory = MemcacheMemory(DEBUG=True)
    @memorize(memory)
    def test(a):
        """test test test!!!"""
        if a > 1:
            return a*test(a-1)
        elif a == 1:
            return 1;
        else:
            return None

    @memorize(memory)
    def fib(n):
        if n == 0 or n == 1:
            return 1
        elif n > 1:
            return fib(n-1) + fib(n - 2)


    print test.__name__
    print test.__class__
    print test.__doc__
    print test(4)
    print test(6)
    print test(-1)
    for i in range(0, 40, 5):
        print fib(i)
