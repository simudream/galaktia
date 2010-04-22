#!/usr/bin/env python
#
# Copyright 2009, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Provides utilities for launching a standalone web socket server.

This file was originally found in mod_pywebsocket module in Google Code.
Modified by Galaktia team.

Note:
This server is derived from SocketServer.ThreadingMixIn. Hence a thread is
used for each request.

"""

import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import logging
import socket
import sys

from mod_pywebsocket import handshake
from mod_pywebsocket import memorizingfile
from mod_pywebsocket import msgutil
from mod_pywebsocket import util

logger = logging.getLogger(__name__)


class _StandaloneConnection(object):
    """Mimic mod_python mp_conn."""

    def __init__(self, request_handler):
        """Construct an instance.

        Args:
            request_handler: A WebSocketRequestHandler instance.
        """
        self._request_handler = request_handler

    def get_local_addr(self):
        """Getter to mimic mp_conn.local_addr."""
        return (self._request_handler.server.server_name,
                self._request_handler.server.server_port)
    local_addr = property(get_local_addr)

    def get_remote_addr(self):
        """Getter to mimic mp_conn.remote_addr.

        Setting the property in __init__ won't work because the request
        handler is not initialized yet there."""
        return self._request_handler.client_address
    remote_addr = property(get_remote_addr)

    def write(self, data):
        """Mimic mp_conn.write()."""
        return self._request_handler.wfile.write(data)

    def read(self, length):
        """Mimic mp_conn.read()."""
        return self._request_handler.rfile.read(length)

    def get_memorized_lines(self):
        """Get memorized lines."""
        return self._request_handler.rfile.get_memorized_lines()


class _StandaloneRequest(object):
    """Mimic mod_python request."""

    def __init__(self, request_handler, use_tls):
        """Construct an instance.

        Args:
            request_handler: A WebSocketRequestHandler instance.
        """
        self._request_handler = request_handler
        self.connection = _StandaloneConnection(request_handler)
        self._use_tls = use_tls
        self._session = None

    def get_uri(self):
        """Getter to mimic request.uri."""
        return self._request_handler.path
    uri = property(get_uri)

    def get_method(self):
        """Getter to mimic request.method."""
        return self._request_handler.command
    method = property(get_method)

    def get_headers_in(self):
        """Getter to mimic request.headers_in."""
        return self._request_handler.headers
    headers_in = property(get_headers_in)

    def is_https(self):
        """Mimic request.is_https()."""
        return self._use_tls


class WebSocketServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """HTTPServer specialized for Web Socket."""

    _DEFAULT_REQUEST_QUEUE_SIZE = 128
    USE_TLS = False
    private_key = None
    certificate = None

    SocketServer.ThreadingMixIn.daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass):
        """Override SocketServer.BaseServer.__init__."""
        if isinstance(server_address, basestring):
            host, port = server_address.split(':', 1)
            server_address = (host, int(port))
        SocketServer.BaseServer.__init__(
                self, server_address, RequestHandlerClass)
        self.request_queue_size = self._DEFAULT_REQUEST_QUEUE_SIZE
        self.socket = self._create_socket()
        self.server_bind()
        self.server_activate()

    def _create_socket(self):
        socket_ = socket.socket(self.address_family, self.socket_type)
        if self.USE_TLS:
            ctx = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
            ctx.use_privatekey_file(self.private_key)
            ctx.use_certificate_file(self.certificate)
            socket_ = OpenSSL.SSL.Connection(ctx, socket_)
        return socket_

    def handle_error(self, request, client_address):
        """Override SocketServer.handle_error."""
        logger.error('Failed to process request from: %r\n%s', \
                client_address, util.get_stack_trace())


class WebSocketRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler specialized for Web Socket."""

    _MAX_MEMORIZED_LINES = 1024 # practically large enough to contain
                                # WebSocket handshake lines.
    USE_TLS = False
    STRICT = False

    def setup(self):
        """Override SocketServer.StreamRequestHandler.setup."""
        self.connection = self.request
        self.rfile = memorizingfile.MemorizingFile(
                socket._fileobject(self.request, 'rb', self.rbufsize),
                max_memorized_lines=self._MAX_MEMORIZED_LINES)
        self.wfile = socket._fileobject(self.request, 'wb', self.wbufsize)

    def __init__(self, *args, **keywords):
        self._request = _StandaloneRequest(self, self.USE_TLS)
        self._handshaker = handshake.Handshaker(self._request, self,
                strict=self.STRICT)
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__( \
                self, *args, **keywords)

    def parse_request(self):
        """Override BaseHTTPServer.BaseHTTPRequestHandler.parse_request.

        Return True to continue processing for HTTP(S), False otherwise.
        """
        result = SimpleHTTPServer.SimpleHTTPRequestHandler.parse_request(self)
        if result:
            try:
                self._handshaker.do_handshake()
                self.transfer_data(self._request)
                return False
            except handshake.HandshakeError, e:
                # Handshake for ws(s) failed. Assume http(s).
                logger.exception('Web socket handshake failed')
                return True
            except Exception, e:
                logger.exception('Error in web socket main transfer loop')
                # logging.info('mod_pywebsocket: %s' % util.get_stack_trace())
                return False
        return result

    def log_request(self, code='-', size='-'):
        """Override BaseHTTPServer.log_request."""
        logger.info('"%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, *args):
        """Override BaseHTTPServer.log_error."""
        # Despite the name, this method is for warnings than for errors.
        # For example, HTTP status code is logged by this method.
        logger.warn('%s - %s', self.address_string(), (args[0] % args[1:]))

    def do_extra_handshake(self, request):
        pass # by default: always accept

    def transfer_data(self, request):
        raise NotImplementedError('Override to implement web socket ' \
                'request handler')

# NOTE: To customize the behavior of a WebSocketServer object,
# bind it to a WebSocketRequestHandler subclass that overrides
# do_extra_handshake and transfer_data methods.

# Example: WebSocketRequestHandler subclass for an echo web socket server:

class EchoWebSocketRequestHandler(WebSocketRequestHandler):
    """ Web socket request handler example for an echo service """
    _GOODBYE_MESSAGE = 'Goodbye'

    def do_extra_handshake(self, request):
        pass # always accept

    def transfer_data(self, request):
        while True:
            line = msgutil.receive_message(request)
            msgutil.send_message(request, line)
            if line == self._GOODBYE_MESSAGE:
                return

def main(program, host='', port=8880):
    # NOTE: To use TLS, check WebSocketServer and WebSocketRequestHandler
    # configuration variables (use_tls, private_key, certificate) and
    # import OpenSSL.SSL
    try:
        bind_address = (host, int(port))
        request_handler = EchoWebSocketRequestHandler
        server = WebSocketServer(bind_address, request_handler)
        server.serve_forever()
    except Exception:
        logger.exception('Failed to run server')
    except KeyboardInterrupt:
        logger.info('Stopped server')

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main(*sys.argv)

# vi:sts=4 sw=4 et
