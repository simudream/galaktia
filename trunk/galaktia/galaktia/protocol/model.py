#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

try:
    import cPickle as pickle
except:
    import pickle

class Datagram(object):
    """ Stores raw datagram bytes to be sent or received to a host and port """

    def __init__(self, data, host=None, port=None):
        """
        :parameters:
            data : str
                Raw bytes
            host : str
                Destination or source host name or IP
            port : int
                Destination or source port number
        """
        self.data, self.host, self.port = data, host, port

    @property
    def destination(self):
        """ :return: 2-tuple with host and port or None if any is None """
        d = (self.host, self.port)
        return d if None not in d else None

class Message(dict):
    """ Represents a message to be sent or received via a protocol """

    def __init__(self, session=None, **kwargs):
        """
        ``Message`` constructor.

        :parameters:
            session : ``Session``
                Session object (contains id, host, port, player_id, etc.)

        :keywords:
            Any key-value pairs to store in the message
        """
        self.session = session
        self['name'] = self.__class__.__name__
        self['timestamp'] = time.time()
        self['ack'] = []
        self.update(kwargs)

    def __hash__(self):
        return hash(self['timestamp'])

    # Semantics of reserved fields:
    #  - name: str representing message class name
    #  - timestamp: float representing message creation time
    #  - ack: list of timestamps that identify acknowledged messages
    #  ...

class Session(object):
    """ Represents a client-server session """

    def __init__(self, id=0, host=None, port=None, character_id=None, \
            secret_key=None, msg_buffer=None, last_activity=None):
        """
        ``Session`` constructor.

        :parameters:
            id : int
                Session identifier (0 reserved as no-session)
            host : str
                Host (associated with the connection to the other endpoint)
            port : int
                Port (associated with the connection to the other endpoint)
            character_id : int
                Character ID
            secret_key : str
                Secret key shared by the 2 connection endpoints for encryption
            msg_buffer : iterable
                Set of pending messages (yet to be acknowledged)
        """
        self.id = id
        self.host = host
        self.port = port
        self.player_id = player_id
        self.secret_key = secret_key
        self.msg_buffer = msg_buffer or MessageBuffer()
        # NOTE: msg_buffer is the only mutable attribute (rest is constant)

class MessageBuffer(object):
    """ Holds acknowledgement and pending messages data for the sake of
        reliability in a message protocol. """

    MAX_SIZE = 1 << 6
    """ :cvar: Max buffer size (for sent messages) """
    MAX_ACKS = 1 << 3
    """ :cvar: Max number of stored acknowledgements """

    def __init__(self):
        """ ``MessageBuffer`` constructor """
        self.buffer = {}
        self.acknowledged = []
        self.last_activity = None
        self._dirty = True

    def update_sent(self, sent_message):
        """
        Stores `sent_message`, i.e., a message to be acknowledged.

        :parameters:
            sent_message : ``Message``
                Message to be acknowledged
        """
        if len(self.buffer) > self.MAX_SIZE:
            raise ValueError('Max message buffer size exceeded')
        t = sent_message['timestamp']
        self.buffer[t] = sent_message
        self._dirty = True

    def update_received(self, received_message):
        """
        Records last session activity and deletes messages according
        to the timestamp and acknowledgements of `received_message`.

        :parameters:
            received_message : ``Message``
                Received message, containing 'timestamp' and 'ack'
        """
        t = received_message['timestamp']
        self.last_activity = max(self.last_activity, t)
        if len(self.acknowledged) > self.MAX_ACKS:
            self.acknowledged.pop(0)
        self.acknowledged.append(t)
        for timestamp in received_message.get('ack', None) or []:
            self.buffer.pop(timestamp, None) # remove item if key found
        self._dirty = True

    def get_pending(self, max_timestamp=None):
        """
        Returns buffered sent messages that were not yet acknowledged.

        :return:
            an iterable of sent messages that were not yet acknowledged
            (to be resent) whose timestamp is less than `max_timestamp`
        """
        if max_timestamp is None:
            return self.buffer.values()
        pending = lambda m: m['timestamp'] < max_timestamp # TODO: optimize
        return filter(pending, self.buffer.values())

    def get_acknowledged(self, max_size=MAX_ACKS):
        """
        Returns acknowledgements of the last received messages.

        :return:
            iterable of floats representing acknowledgements of the last
            received messages
        """
        return self.acknowledged[:max_size]

class SessionDAO(object):
    """ Data Access Object for ``Session`` objects """

    def __init__(self):
        """ ``SessionDAO`` constructor """
        self._sessions = {} # TODO: replace storage by memcached client
        # NOTE: pickling is unnecessary in this implementation but not
        # in the case of storing sessions via memcached

    def get(self, id):
        """ :return: ``Session`` object identified by `id` """
        serialized = self._sessions[id]
        return pickle.loads(serialized)

    def set(self, session):
        """ Stores `session` """
        if not session.msg_buffer._dirty:
            return
        # TODO: mutex (race condition between session DAOs in parallel)
        serialized = pickle.dumps(session)
        self._sessions[session.id] = pickle.dumps(serialized)
        self.session.msg_buffer._dirty = False

    def create(self, **kwargs):
        """ :return: Newly created session (with unique id) """
        id = max(self._sessions.keys() or [0]) + 1
        return Session(id=id, **kwargs)

    def get_by(self, user_id):
        # TODO: this is a hack for compatibility with old SessionDAO API
        for session in self._sessions.values():
            if session.character_id == user_id:
                return session
        return None

    def get_logged(self):
        # TODO: this is a hack for compatibility with old SessionDAO API
        return self._sessions.values()

    def delete(self, session):
        # TODO: this is a hack for compatibility with old SessionDAO API
        self._sessions.pop(id, None)

