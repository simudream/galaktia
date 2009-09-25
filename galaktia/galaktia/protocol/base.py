#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

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
                Converts ``Datagram`` to ``Message`` and viceversa
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
                    host, port, datagram)
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
            self.transport.write(datagram.data, datagram.destination)
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

    self.TIMEOUT = 60 # 1 minute

    def __init__(self, codec, controller, message_dao):
        BaseServer.__init__(self, codec, controller)
        self.message_dao = message_dao

    def on_receive(self, input_message):
        msg_buffer = input_message.session.msg_buffer
        msg_buffer.update_received(input_message)

    def on_send(self, output_message):
        msg_buffer = output_message.session.msg_buffer
        output_message['ack'] = msg_buffer.get_acknowledged()
        msg_buffer.update_sent(output_message)
        self.schedule(self.get_timeout_callback(msg_buffer))

    def schedule(self, callback):
        pass # TODO: set timer to run callback in self.TIMEOUT seconds

    def get_timeout_callback(self, msg_buffer):
        server = self
        def callback(self, server=server, msg_buffer=msg_buffer):
            for message in msg_buffer.get_pending(time.time() - self.TIMEOUT):
                server.send(message)
        return callback

