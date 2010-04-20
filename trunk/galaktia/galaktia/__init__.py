#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from controlfreak.commands import BaseAction, BaseShellAction
from controlfreak.commands import MultiActionCommand

class GalaktiaServerCommand(BaseAction):
    name = 'server'
    description = 'Galaktia game server'

    def run(self, appctx):
        server = appctx.get('server::server')
        raise NotImplementedError('Not yet implemented')

class GalaktiaShellCommand(BaseShellAction):
    name = 'shell'
    description = 'Galaktia shell (provides application context)'
    BANNER = """

Galaktia shell

Available variables:
  - appctx : Application context
"""

main = MultiActionCommand(GalaktiaShellCommand(), GalaktiaServerCommand())
