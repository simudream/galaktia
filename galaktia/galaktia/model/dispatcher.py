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



class ExtendableDispatcherController(BaseDispatcherController):
    """ A Dispatcher Controller that can scan for available controllers and
        (un)plug one or several of them during runtime.

        To work with this Dispatcher, controller classes must define a static
        variable MESSAGE_TYPE containing the type of message they intend to
        handle.
    """

    DEFAULT_MODULE = 'galaktia.controller'

    def __init__(self, dao, routes = None):
        self.routes = routes or {}
        self.scanned = []

    def plug(self, controller):
        """ Plugs a controller, routing all messages of controller.MESSAGE_TYPE
            to it.
        """
        try:
            if controller.MESSAGE_TYPE not in self.routes:
                self.routes[controller.MESSAGE_TYPE] = controller
            else:
                logger.exception("Did not load %s. Conflict over message type %s." 
                                 % (str(controller, str(MESSAGE_TYPE))))
                                 
        except:
            logger.exception("Error while loading %s." % str(controller))


    def unplug(self, message_type):
        """ Unplugs the controller currently handling message_type, """
        # WARNING: NOT A SINGLE CHARACTER OF THIS METHOD IS THREAD-SAFE.
        if message_type in self.routes:
            del self.routes[message_type]

    def plugAll(self, module = DEFAULT_MODULE):
        """ Plugs all the controllers found in the given module. """
        for controller in self.scan(module):
            self.plug(controller)

    def unplugAll(self):
        """ Unplugs all controllers. """
        # WARNING: NOT A SINGLE CHARACTER OF THIS METHOD IS THREAD-SAFE.
        self.routes.clear()        

    def scan(self, module = DEFAULT_MODULE):
        """Scans the given module for controllers."""

        # Borrowed from Coffey. I loved this lambda/reduce, man! Neat!
        # This gets the actual module object from the string module name:
        to_import = reduce(lambda mod, submod: getattr(mod, submod),
                           module.split('.')[1:], __import__(module))

        # Now, the imported module can either be a proper .py, or a directory
        # package. Let's find out and get those controllers:
        
        if os.path.basename(to_import.__file__).startswith("__init__.py"):
        
            # We were given a package. We need to scan every file in it.
            scanlist = \
            map(lambda f: f.split(".")[0], 
                filter(lambda f: f.endswith(".py") and not f.startswith("_"),
                       os.listdir(to_import.__path__[0])))

            # Now scanlist holds a list of .py modules in the package. Let's
            # import the package requesting all of those module as fromlist:
            imported = __import__(module, fromlist = scanlist)

            # Now, imported holds a lot of extra variables, we want to get the
            # actual modules found in the package from among those:
            submodules = [getattr(imported, attr) for attr in 
                          filter(lambda attr: not attr.startswith("_"),
                                 dir(imported))]

        else:

            # Not a package, but a single .py file. Much, much easier. Behold:
            submodules = [to_import]

        # Excelent. Whether we have one or several modules, we need to scan
        # for subclasses of Controller (other than Controller itself):
        controllers = []
        
        for mod in submodules:
            object_names = filter(lambda name: not name.startswith("_"),
                                  dir(mod))
                                  
            controllers += filter(lambda obj: issubclass(obj, Controller) and
                                              obj is not Controller,
                                  [getattr(mod, obj) for obj in object_names])

        return controllers
                
    def get_controller_for(self, message):
        return self.routes[message.__class__.__name__]


