#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, logging

from twisted.internet import reactor
from twisted.python import log

from galaktia.protocol.model import Datagram, Message
from galaktia.protocol.base import BaseServer, BaseClient
from galaktia.protocol.codec import ProtocolCodec

logger = logging.getLogger(__name__)

class Controller(object):

    def greet(self):
        """ Returns Message objects to be sent to start a connection """
        return [] # override in clients to start a connection

    def process(self, input_message):
        """ Returns an iterable of output messages in response to input """
        raise NotImplementedError


