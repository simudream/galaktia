#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Base server model and implementation.
"""

import logging

from mod_pywebsocket import msgutil

from galaktia.model.standalone import WebSocketRequestHandler

logger = logging.getLogger(__name__)

class BaseServer(WebSocketRequestHandler):
    """ Base class for a web sockets server """

    def __init__(self, codec, controller):
        """
        BaseServer constructor.

        :parameters:
            codec : Codec
                Converts ``str`` to ``Message`` and viceversa
            controller : Controller
                Implements a message handling method
        """
        self.codec = codec
        self.controller = controller
        self._receive = None
        self._send = None

    def do_extra_handshake(self, request):
        """ Performs extra validation on handshake """
        pass # always accept # TODO: do extra login validation

    def transfer_data(self, request):
        """ Runs web socket request handler main loop """
        while True:
            try:
                self.handle(request)
            except StopIteration:
                break
            except Exception:
                logger.exception('Fatal error handling request: %r', request)

    def handle(self, request):
        """ Performs a receive/send step of the request handler main loop  """
        input_string = msgutil.receive_message(request)
        input_message = self.codec.decode(input_string)
        self.receive(request, input_message)

    def receive(self, request, input_message):
        """ Receives an input message to be handled by controller """
        logger.debug('Received from %r: %s', request, input_message)
        for output_message in self.controller.handle(input_message):
            self.send(request, output_message)

    def send(self, request, output_message):
        """ Sends output messages returned by controller """
        output_string = self.codec.encode(output_message)
        msgutil.send_message(request, output_string)
        logger.debug('Sent to %r: %s', request, output_message)

