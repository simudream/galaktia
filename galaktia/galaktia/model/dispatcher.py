#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import os

from galaktia.model.controller import BaseDispatcherController

class DispatcherController(BaseDispatcherController):
    """ A dispatcher controller that can handle messages whose class name
        ends with "RequestMessage" by dispatching them to the controller
        whose class has the same name but ends with "Controller". """

    # Mmmmm... Not very elegant... Dispathing by class name is a bit hacky :P

    BASE_MODULE = 'galaktia.controller'
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
        
        if os.path.basename(to_import.__file__).startswith("__init__.py"): # can also be .pyc
        
            # We were given a package. We need to scan every file in it.
            scanlist = map(lambda f: f.split(".")[0], 
                           filter(lambda f: f.endswith(".py") and not f.startswith("_"),
                                  os.listdir(to_import.__path__[0])))

            # Now scanlist holds a list of .py modules in the package. Let's
            # import the package requesting all of those module as fromlist:
            imported = __import__(module, fromlist = scanlist)

            # Now, imported holds a lot of extra variables, we want to get the
            # actual modules found in the package from among those:
            submodules = [getattr(imported, attr) for attr in 
                          filter(lambda attr: not attr.startswith("_"), dir(imported))]

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


