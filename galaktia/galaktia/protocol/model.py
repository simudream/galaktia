#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

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

    def __str__(self):
        return '\n{Objeto Datagrama: \n \tData=%s \n \tHost=%s \n \tPort=%s}\n'%(self.data, self.host, self.port)
        # WTF is this for?? Maybe self.__repr__...

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
                Session object (contains id, host, port, character_id, etc.)

        :keywords:
            Any key-value pairs to store in the message
        """
        self.session = session # session won't be in kwargs
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
            secret_key=None):
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
        """
        self.id = id
        self.host = host
        self.port = port
        self.character_id = character_id
        self.secret_key = secret_key
        # NOTE: no session attribute should be altered after construction

    def __str__(self):
        retstr = ' { Objeto Session: \n \t ID = '+str(id)
        retstr += '\n\tHost, Port = '+str(host)+','+str(port)
        retstr += '\n\tcharacter_id = '+str(character_id)+' } '

class MessageBuffer(object):
    """ Holds acknowledgement and pending messages data for the sake of
        reliability in a message protocol. """

    MAX_SIZE = 1 << 6
    """ :cvar: Max buffer size (for sent messages) """
    MAX_ACKS = 1 << 3
    """ :cvar: Max number of stored acknowledgements """

    def __init__(self):
        """ ``MessageBuffer`` constructor """
        self.sent = {}
        self.received = []
        self.last_activity = None
        self._dirty = True

    def update_sent(self, sent_message):
        """
        Stores `sent_message`, i.e., a message to be acknowledged.

        :parameters:
            sent_message : ``Message``
                Message to be acknowledged
        """
        if len(self.sent) > self.MAX_SIZE:
            raise ValueError('Max message buffer size exceeded')
        t = sent_message['timestamp']
        self.sent[t] = sent_message
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
        if len(self.received) > self.MAX_ACKS:
            self.received.pop(0)
        self.received.append(t)
        for timestamp in received_message.get('ack', []):
            self.sent.pop(timestamp, None) # remove item if key found
        self._dirty = True

    def get_pending(self):
        """
        Returns buffered sent messages that were not yet acknowledged.

        :return:
            an iterable of sent messages not yet acknowledged (to be resent)
        """
        for m in self.sent.itervalues():
            yield m

    def get_acknowledged(self, max_size=MAX_ACKS):
        """
        Returns acknowledgements of the last received messages.

        :return:
            list of floats representing acknowledgements of the last
            received messages
        """
        return self.received[:max_size]

class SessionDAO(object):
    """ Data Access Object for ``Session`` objects """
    # TODO: replace by memcached storage implementation
    # TODO: mutex locking (race condition between session DAOs in parallel)
    #       http://en.wikipedia.org/wiki/Producer-consumer_problem
    # NOTE: sessions should not be modified after creation

    def __init__(self):
        """ ``SessionDAO`` constructor """
        self._sessions = {} # TODO: replace storage by memcached client

    def get(self, id):
        """ :return: ``Session`` object identified by `id` """
        return self._sessions.get(id)

    def set(self, session):
        """ Stores `session` """
        self._sessions[session.id] = session

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

class MessageBufferDAO(object):
    """ Data Access Object for ``MessageBuffer`` objects """
    # TODO: replace by memcached storage implementation
    # TODO: mutex locking (race condition between session DAOs in parallel)
    #       http://en.wikipedia.org/wiki/Producer-consumer_problem

    def __init__(self):
        """ ``MessageBufferDAO`` constructor """
        self._buffers = {}

    def get(self, session_id):
        """ :return: ``MessageBuffer`` object for given session ID """
        return self._buffers.get(session_id)

    def set(self, session_id, msg_buffer):
        """ Sets the ``MessageBuffer`` object for given session ID """
        if msg_buffer._dirty:
            msg_buffer._dirty = False
            self._buffers[session_id] = msg_buffer

