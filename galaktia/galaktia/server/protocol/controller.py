#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log

from galaktia.server.protocol.model import Datagram, Message
from galaktia.server.protocol.base import BaseServer, BaseClient
from galaktia.server.protocol.codec import ProtocolCodec

logger = logging.getLogger(__name__)

class Controller(object):

    def greet(self):
        """ Returns Message objects to be sent to start a connection """
        return [] # override in clients to start a connection

    def process(self, input_message):
        """ Returns an iterable of output messages in response to input """
        raise NotImplementedError


class AcknowledgeController(Controller):
    
    def __init__(self):
        self._pendingAcknowledge = []

    def acknowledged(self, message_id):
        self._pendingAcknowledge.remove(message_id)