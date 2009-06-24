#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from twisted.internet.protocol import DatagramProtocol

from galaktia.server.protocol.model import Datagram, Message

logger = logging.getLogger(__name__)

class BaseServer(DatagramProtocol):
    """ Base class for a datagram protocol server """

    def __init__(self, codec, controller):
        """
        BaseServer constructor.

        :parameters:
            codec : Codec
                Converts Datagram to Message and viceversa
            controller : Controller
                Implements a message processing method
        """
        self.codec = codec
        self.controller = controller

    def datagramReceived(self, input_data, (host, port)):
        """ Event handler for datagram reception """
        input_message = self.codec.decode(Datagram(input_data, host, port))
        logger.debug('Received from %s:%d: %s', host, port, input_message)
        for output_message in self.controller.process(input_message):
            self.send(output_message)

    def send(self, output_message):
        """ Sends an output message (according to its host, port) """
        destination = tuple(output_message[i] for i in ('host', 'port')) \
                if output_message.get('host') else None
        self.transport.write(self.encode(output_message), destination)
        logger.debug('Sent to %s: %s', destination or 'server', \
                output_message)

class BaseClient(BaseServer):
    """ Base class for a datagram protocol client """

    DEFAULT_SERVER = '127.0.0.1'
    DEFAULT_PORT = 6414

    def __init__(self, codec, controller, \
            server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """ BaseClient constructor """
        super(BaseClient, self).__init__(codec, controller)
        self.server = server
        self.port = int(port)

    def startProtocol(self):
        """ Triggers the first message sent by client on a session """
        self.transport.connect(self.server, self.port)
        for output_message in self.controller.greet():
            self.send(output_message)

    def connectionRefused(self):
        """ Event handler for refused connections (no server listening) """
        logger.error('No server listening at %s:%d', self.server, self.port)

