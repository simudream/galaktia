#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__='restructuredtext'

from controlfreak.commands import MultiActionCommand, \
        BaseAction, BaseShellAction

class GalaktiaServerCommand(BaseAction):
    name = 'server'
    description = 'Galaktia game server'

    def run(self, appctx):
        pass # TODO

class GalaktiaClientCommand(BaseAction):
    name = 'client'
    description = 'Galaktia game client'

    def run(self, appctx):
        pass # TODO

class GalaktiaShellCommand(BaseShellAction):
    name = 'shell'
    description = 'Galaktia shell (provides application context)'
    BANNER = """

Galaktia shell

Available variables:
  - appctx : Application context
"""

main = MultiActionCommand(GalaktiaShellCommand())
