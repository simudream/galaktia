# Add header...

import heapq
from time import time
PROCESS_MODULE="threading"
if PROCESS_MODULE == "threading":
    from threading import Condition, Thread
else:
    from multiprocessing import Condition, Thread
# AWESOME IDEA: Make this compatible with multiprocessing.


class MessageQueue(object):
    """
        A priority queue that supports elements with Time To Live or expiration
        date. A simple way to enable unidirectional data transports or pipes.
    """

    def __init__(self):
        self.queue = []
        self.cond = Condition()

    def put(self, item):
        self.xput(item)

    def xput(self, action, priority=1, expire=300):
        """
            Add an action to the queue with priority and expiration date.
        """
        self.cond.acquire()
        heapq.heappush( self.queue, \
                (priority, time() + expire, action))
        self.cond.notify()
        self.cond.release()

    def get(self, block=True):
        self.cond.acquire()
        if (len(self.queue) == 0):
            if (block == True):
                self.cond.wait()
            else:
                return None
        priority, expiration, action = heapq.heappop(self.queue)
        self.cond.release()
        if time() > expiration:
            return self.get(block)
        else:
            return action

    def next(self):
        return self.get(False)

    def has_items(self):
        return (True if len(self.queue) > 0 else False)


class BaseEngine(Thread):
    """
        BaseEngine provides the basic functionality needed by any Engine in the
        game.
    """

    def __init__(self, handlers):
        Thread.__init__(self)
        self.__input = MessageQueue()
        self.handlers = handlers

    def _pack(self, action, data):
        return {'type':action, 'data': data}

    def _request(self, priority, expire, action, callback, caller):
        self.__input.xput(priority, expire,(action, callback, caller))

    def run(self):
        while True:
            action, callback, caller = self.__input.get()
            try:
                handler = self.handlers[action[type]]
                handler(callback, caller, action['data'])
            except:
                pass
                # TODO: I know, errors should never blah, blah, blah...

