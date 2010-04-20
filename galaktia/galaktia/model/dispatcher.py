#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import os

from galaktia.server.model.controller import BaseDispatcherController

class DispatcherController(BaseDispatcherController):
    """ A dispatcher controller that can handle messages whose class name
        ends with "RequestMessage" by dispatching them to the controller
        whose class has the same name but ends with "Controller". """

    # Mmmmm... Not very elegant... Dispathing by class name is a bit hacky :P

    BASE_MODULE = 'galaktia.server.controllers'
    CONTROLLER_NAME = '%sController'
    MESSAGE_NAME = '%sRequestMessage'

    def __init__(self, dao, base_module=BASE_MODULE, **extra_routes):
        self.routes = extra_routes or {}
        for module in self._locate_submodules(base_module):
            name = module.title()
            imported = __import__('.'.join((base_module, module)), \
                    fromlist=[self.CONTROLLER_NAME % name])
            controller = getattr(imported, self.CONTROLLER_NAME % name)()
            controller.dao = dao
            self.routes[self.MESSAGE_NAME % name] = controller

    def _locate_submodules(self, base_module):
        imported = reduce(lambda imported, path: getattr(imported, path), \
                base_module.split('.')[1:], __import__(base_module))
        path = os.path.abspath(os.path.dirname(imported.__file__))
        for filename in os.listdir(path):
            if filename.endswith('.py') and not filename.startswith('_'):
                yield filename[:-3]

    def get_controller_for(self, message):
        return self.routes[message.__class__.__name__]

