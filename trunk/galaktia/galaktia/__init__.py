#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

import logging
import os

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

class GalaktiaCommand(MultiActionCommand):
    """ Custom MultiActionCommand with default configuration """

    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config')
    ACTION_CLASSES = [
        GalaktiaShellCommand,
        GalaktiaServerCommand,
        GalaktiaClientCommand
    ]

    def __init__(self):
        actions = [cls() for cls in self.ACTION_CLASSES]
        super(GalaktiaCommand, self).__init__(*actions)

    def customCommandLineValidation(self, parser):
        super(GalaktiaCommand, self).customCommandLineValidation(parser)
        # sets default freakconfig option in case '-c' option is omitted
        if self.options.freakconfig is None:
            self.options.freakconfig = os.path.join(self.CONFIG_PATH, \
                    'galaktia-application.yaml')

# Main program
main = GalaktiaCommand()
