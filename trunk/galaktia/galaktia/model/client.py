#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

"""Utilities for Galaktia client: running web server, launching GUI in
Google Chrome, etc."""

import BaseHTTPServer
import SimpleHTTPServer
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser

logger = logging.getLogger(__name__)

def _find_binary(name):
    pipe = subprocess.Popen(['which', name], stdout=subprocess.PIPE)
    return pipe.communicate()[0].rstrip('\n') or None

def _find_browser():
    """ Locates Google Chrome browser (or else default web browser) """
    if sys.platform == 'darwin':
        bin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                # most Mac OS X users will locate Google Chrome at this path
    else:
        bin = _find_binary('google-chrome')
                # works for Linux/UNIX systems with this binary in env $PATH
    hint = bin.replace(' ', '\\ ') + ' %s' if bin is not None \
            and os.path.isfile(bin) else None
    return webbrowser.get(hint) # picks default browser if hint is None
            # NOTE: works for Windows if Google Chrome is the default browser

def run_client_web_server(path=None, server_address=None):
    """ Runs a SimpleHTTPServer at the web assets path """
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
    browse = lambda: time.sleep(1) or _find_browser().open(url, new=2)
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

