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


class OutOfBounds(Exception):
    pass

#
#   PSEUDO-INTERFACES
#


class Memorized(object):
    """ This class wraps a normal callable and returns a memorized callable
        with a "memo" storage. End users are not intended to know what happens
        inside this class, neither they should know about it.

    """

    def __init__(self, f, memo, debug=False):
        self.__f = f
        self.__memo = memo
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memorized Callable %s" % f.__name__)
        if debug:
            self.log.setLevel(logging.DEBUG)

    def __create_key(self, f, *args, **kwargs):
#       TODO: Is there another way to create a key?
        the_hash = md5(f.__name__)
        for arg in args:
            the_hash.update(str(arg))
        the_hash.update("|")
        for key, val in kwargs.iteritems():
            the_hash.update("%s:%s;".__mod__(key, val))
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


class Memory(object):
    """
        Memory objects are key-value gateways to a database or any other kind
       of memory storage. They behave the same way dictionaries do, which
       makes it easier to mock them.

        Required methods are __getitem__, __setitem__ and __delitem__.

        A convenience method __call__ is defined to use objects of this class
        as decorators. Doing so will apply the memorize pattern to the
        function. You can find more information in the corresponding docstring
        in __call__.

    """

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __call__(self, f):
        """
            This is a convenience function that provides the Memory Pattern as
            a decorator and wraps it in a way transparent to the end user
            (i.e.: they will not know whether the function has been decorated
            or not). This is acomplished by using the "wrap" decorator in
            functools.

        """
        memo = Memorized(f, self)
        wraps(f)(memo)
        return memo


class MemoryPool(Memory):
    """
        A MemoryPool object provides an extended way of using Memory gateways.
        It holds more than one connection open, so it should be theoretically
        faster than ad-hoc connections. However, it does not necessarily imply
        that the objects in the pool are connected to different servers.

        It *must* behave like a Memory gateway too, masking the
        lock/hold/return operations inside the MemoryPool, providing a complete
        replacement for normal Memory objects.
    """

    def count(self):
        raise NotImplementedError

    def grow(self, number=1):
        raise NotImplementedError

    def shrink(self, number=1):
        raise NotImplementedError

#
#   DECORATORS AND FACTORIES
#


class memorize(object):

    def __init__(self, memory, debug=False):
        self._memory = memory
        self.debug = debug

    def __call__(self, f):
        memo = Memorized(f, self._memory, self.debug)
        wraps(f)(memo)
        return memo


#
#   CONCRETE STORAGES
#


class MemcacheMemory(Memory):
    """
        Memory gateway to a Memcache server
    """

    def __init__(self, servers=["127.0.0.1:11211"], expire=0, debug=False):
        """
            :param servers: List of servers to use. Please, read
            memcache.Client help.

        """
#        super(MemcacheMemory, self).__init__()
        self._client = MemcacheClient(servers)
        self._expire = expire
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memcache-Gateway")
        if debug:
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
        self._client.set(key, value, self._expire)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        if self._client.delete(key) == 0:
            raise KeyError


class MemcacheMemoryPool(MemoryPool):

    def __init__(self, servers=["127.0.0.1:11211"], expire=0, upper_limit=100,
            lower_limit=1, debug=False):
#        super(MemcacheMemoryPool, self).__init__()
        self._clients = [MemcacheMemory(servers=servers, expire=expire) for o
                in xrange(0, upper_limit / 2)]
        self.__expire = expire
        self._servers = servers
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memcache Pool")
        self.__debug = debug
        self.__clients_lock = Lock()
        if debug:
            self.log.setLevel(logging.DEBUG)

    def __expire_get(self):
        return self.__expire

    def __expire_set(self, value):
        if self.__expire != value:
            self.__expire = value
            for i in self._clients:
                i._expire = value

    _expire = property(__expire_get, __expire_set)


    def count(self):
        try:
            self.__clients_lock.acquire()
            return len(self._clients)
        finally:
            self.__clients_lock.release()

    def grow(self, number=1):
        self.log.debug("Adding %s new servers to the pool", number)
        for i in range(number):
            self._clients.append[MemcacheMemory(self._servers, self._expire,
                    self.__debug)]

    def shrink(self, number=1):
        self.log.debug("Deleting %s servers from the pool", number)
        self.__clients_lock.acquire()
        for i in range(number):
            self._clients.pop()
        self.__clients_lock.release()

    def __claim_client(self):
        if self.count() < self.lower_limit:
            self.grow()
        try:
            self.__clients_lock.acquire()
            return self._clients.pop()
        finally:
            self.__clients_lock.release()

    def __return_client(self, client):
        if self.count() < self.upper_limit:
            self.__clients_lock.acquire()
            self._clients.append(client)
            self.__clients_lock.release()

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        try:
            client = self.__claim_client()
            return client[key]
        finally:
            self.__return_client(client)

    def __setitem__(self, key, value):
        self.log.debug("Setting key %s to %s", key, value)
        try:
            client = self.__claim_client()
            client[key] = value
        finally:
            self.__return_client(client)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        try:
            client = self.__claim_client()
            client.__delitem__(key)
        finally:
            self.__return_client(client)


class RedisMemory(Memory):
    """
        Memory gateway to a Redis server
    """

    def __init__(self, host=None, port=None, expire=None, debug=False,
                *args, **kwargs):
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
        if debug:
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
        self.log.debug("Setting expire time to %s seconds for key %s",
                time, key)
        self._client.expire(key, time)



#
#   Tests?
#


if __name__ == "__main__":
    memory = MemcacheMemoryPool(debug=True, expire=2)

    @memorize(memory)
    def test(a):
        """test test test!!!"""
        if a > 1:
            return a * test(a - 1)
        elif a == 1:
            return 1
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

    @memory
    def test(i):
        return i

    from time import sleep
    print test("a")
    sleep(1)
    print test("a")
    memory._expire = 3
    sleep(3)
    print test("a")
    sleep(4)
    print test("a")
