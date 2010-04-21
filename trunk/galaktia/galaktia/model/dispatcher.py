#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import logging
import os
from pkgutil import iter_modules

import galaktia.controller
from galaktia.model.controller import Controller, BaseDispatcherController
from galaktia.model.message import RequestMessage

logger = logging.getLogger(__name__)

class DispatcherController(BaseDispatcherController):
    """ A dispatcher controller that can handle messages of a
        ``RequestMessage`` subclass by dispatching them to the
        controller of a ``Controller`` subclass in the same module. """

    def __init__(self, dao, package=galaktia.controller, **extra_routes):
        self.routes = extra_routes or {}
        for i in iter_modules(package.__path__, package.__name__ + '.'):
            try:
                module = __import__(i[1], fromlist=['__name__'])
                controller = self._find_subclass(module, Controller)()
                message_class = self._find_subclass(module, RequestMessage)
                controller.dao = dao
                self.routes[message_class.__name__] = controller
            except Exception, e:
                logger.warn('Skipped dispatcher routing for module %r: %s', \
                        i[1], e)

    def _find_subclass(self, module, base_class):
        for attr in dir(module):
            subclass = getattr(module, attr)
            if not isinstance(subclass, dict) and subclass != base_class and \
                    issubclass(subclass, base_class):
                return subclass
        raise LookupError('No subclass of %r in %r' % (base_class, module))

    def get_controller_for(self, message):
        return self.routes[message.__class__.__name__]
            # NOTE: we could index by class instead of by class name (str)

