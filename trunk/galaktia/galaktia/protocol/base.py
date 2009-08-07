#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from twisted.internet.protocol import DatagramProtocol

from galaktia.protocol.model import Datagram, Message

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
        datagram = Datagram(input_data, host, port)
        try:
            input_message = self.codec.decode(datagram)
            logger.debug('Received from %s:%d: %s', host, port, input_message)
        except Exception:
            logger.exception('Failed to decode datagram from %s:%d: %s', \
                    host, port, input_message)
            return
        #self.dispatch_events('on_receive', input_message)
        self.on_receive(input_message)
        for output_message in self.controller.process(input_message):
            self.send(output_message)

    def send(self, output_message):
        """ Sends an output message (according to its host, port) """
        #self.dispatch_events('on_send', output_message)
        self.on_send(output_message)
        try:
            datagram = self.codec.encode(output_message)
        except Exception:
            logger.exception('Failed to encode message: %s', output_message)
            return
        try:
            destination = datagram.get_destination()
            self.transport.write(datagram.data, destination)
            logger.debug('Sent to %s: %s', destination or 'server', \
                    output_message)
        except Exception:
            logger.exception('Failed to send message: %s', output_message)

    def on_receive(self, input_message):
        """ Extensible method for event listeners """

    def on_send(self, output_message):
        """ Extensible method for event listeners """

class BaseClient(BaseServer):
    """ Base class for a datagram protocol client """

    DEFAULT_SERVER = '127.0.0.1'
    DEFAULT_PORT = 6414

    def __init__(self, codec, controller, \
            server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """ BaseClient constructor """
        BaseServer.__init__(self, codec, controller) # old-style class
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

class ReliableServer(BaseServer):
    """ Implements a reliability layer on BaseServer """

    def __init__(self, codec, controller, message_dao):
        BaseServer.__init__(self, codec, controller)
        self.message_dao = message_dao

    def on_receive(self, input_message):
        if 'ack' in input_message:
            message = self.message_dao.get_message_for_ack(input_message)
            if message is not None:
                self.message_dao.delete(message)
        else:
            ack = self.message_dao.get_ack_for_message(input_message)
            if ack is None:
                ack = input_message.acknowledge()
                if ack is not None:
                    self.send(ack) # send adds message to DAO

    def on_send(self, output_message):
        self.message_dao.put(output_message)

    def on_timeout(self):
        # should be called on regular intervals (e.g.: every 60 seconds)
        TIMEOUT = 60 # 1 minute
        self.message_dao.clean_acks(8 * TIMEOUT)
        unacknowledged = self.message_dao.get_unacknowleged_messages(TIMEOUT)
        for message in unacknowledged:
            self.send(message)

