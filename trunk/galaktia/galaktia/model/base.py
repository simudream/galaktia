#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Base model for server request handlers.
"""

import logging

from mod_pywebsocket import msgutil

from galaktia.model.standalone import WebSocketServer, WebSocketRequestHandler

logger = logging.getLogger(__name__)

def make_request_handler_factory(codec, controller, session_dao):
    """ :return: callable that returns RequestHandlerAdapter instances
                 configured with given args """
    return lambda *args, **kwargs: RequestHandlerAdapter(codec, \
            controller, session_dao, *args, **kwargs)

class RequestHandlerAdapter(WebSocketRequestHandler):
    """ Adapts WebSocketRequestHandler to galaktia.model """

    codec = None
    """ :ivar: ``Codec`` that converts ``str`` to ``Message`` and viceversa """
    controller = None
    """ :ivar: ``Controller`` that handles ``Message`` instances """
    session_dao = None
    """ :ivar: ``SessionDAO`` that maps sessions to requests """

    def __init__(self, codec, controller, session_dao, *args, **kwargs):
        """ WebSocketRequestHandler adapter that fits galaktia.model """
        self.codec = codec
        self.controller = controller
        self.session_dao = session_dao
        WebSocketRequestHandler.__init__(self, *args, **kwargs)

    def do_extra_handshake(self, request):
        """ Performs extra validation on handshake """
        pass # always accept # TODO: do extra login validation?

    def transfer_data(self, request):
        """ Runs web socket request handler main loop """
        # NOTE: request == self._request
        while True:
            try:
                self._transfer_data()
            except StopIteration:
                break # close socket
            except msgutil.MsgUtilException:
                logger.exception('Web socket closed')
                break # close socket
            except Exception:
                logger.exception('Fatal error handling request: %r', request)

    def _transfer_data(self):
        """ Performs a receive/send step of the request handler main loop  """
        input_string = msgutil.receive_message(self._request)
        input_message = self.codec.decode(input_string)
        for output_message in self.receive(input_message):
            self.send(output_message)

    def receive(self, input_message):
        """ Receives an input message to be handled by controller """
        request = self._request
        input_message._src_session = self.session_dao.get_session(request)
        logger.debug('Received from %r: %s', request, input_message)
        return self.controller.handle(input_message)

    def send(self, output_message):
        """ Sends output messages returned by controller """
        request = self.session_dao.get_request(output_message, self._request)
        output_string = self.codec.encode(output_message)
        msgutil.send_message(request, output_string)
        logger.debug('Sent to %r: %s', request, output_message)

class SessionDAO(dict):
    """ Session DAO. Maps sessions to requests """

    # Not sure if all this works...

    def get_request(self, message, current_request):
        if current_request not in self:
            if message._src_session != message._dst_session:
                raise ValueError('First message of a new session must be ' \
                        'sent to the same session')
            self[message._src_session] = current_request
            current_request._session = message._src_session
        elif message._src_session < 0: # TODO: decide how to close session
            raise StopIteration('Session closed')
        return self[message._dst_session]

    def get_session(self, request):
        return request._session

