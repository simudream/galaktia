#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from mod_pywebsocket.standalone import _main

def main(program, port=6414):
    """ Main program: Starts a server on given port """
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    _main()

if __name__ == '__main__':
    # XXX print 'Usage: python -m galaktia.server.main [port]'
    main(*sys.argv)

    # TEMPORARILY NEW INVOKATION:
    # python -m galaktia.server.main -p 6414 -d ./websocket --allow-draft75
    # TODO: adapt mod_pywebsocket.standalone._main

