#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

"""Utilities for Galaktia client: launching web server, etc."""

import BaseHTTPServer
import SimpleHTTPServer
import logging
import os
import sys
import threading
import time
import webbrowser

logger = logging.getLogger(__name__)

def run_client_web_server(path=None, server_address=None):
    """ Runs a SimpleHTTPServer at the web assets path """
    # TODO: detect Google Chrome binary and launch in bg via webbrowser
    # TODO: detect dev_appserver.py to launch server via GAE SDK
    if path is None:
        heredir = os.path.dirname(__file__)
        path = os.path.join(heredir, '..', '..', '..', 'web', 'assets')
    os.chdir(os.path.abspath(path)) # document root hack
    if server_address is None:
        server_address = ('', 8000)
    elif isinstance(server_address, basestring):
        host, port = server_address.rsplit(':', 1)
        server_address = (host, int(port))
    server = BaseHTTPServer.HTTPServer(server_address, \
            SimpleHTTPServer.SimpleHTTPRequestHandler)
    url = 'http://%s:%s' % server.socket.getsockname()
    browse = lambda: time.sleep(1) or webbrowser.open(url, new=2)
    thread = threading.Thread(target=browse)
    thread.start() # defers opening web browser after running server
    try:
        logger.info('Starting Galaktia client web server at %s:%s', \
                *server.socket.getsockname())
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Stopped Galaktia client web server')
    thread.join()

def main(program, *args):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    run_client_web_server(*args)

if __name__ == '__main__':
    main(*sys.argv)

