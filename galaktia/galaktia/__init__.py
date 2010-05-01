#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

import logging

from controlfreak.commands import BaseAction, BaseShellAction
from controlfreak.commands import MultiActionCommand

from galaktia.model.client import run_client_web_server

logger = logging.getLogger(__name__)

class GalaktiaServerCommand(BaseAction):
    name = 'server'
    description = 'Galaktia game server'

    def run(self, appctx):
        server = appctx.get('server::server')
        logger.info('Starting Galaktia server at %s:%s', \
                *server.server_address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info('Stopped Galaktia server')

class GalaktiaClientCommand(BaseAction):
    name = 'client'
    description = 'Galaktia game client'

    def run(self, appctx):
        run_client_web_server() # TODO: custom path and server address

class GalaktiaShellCommand(BaseShellAction):
    name = 'shell'
    description = 'Galaktia shell (provides application context)'
    BANNER = """

Galaktia shell

Available variables:
  - appctx : Application context
"""

main = MultiActionCommand(GalaktiaShellCommand(), \
        GalaktiaServerCommand(), GalaktiaClientCommand())
