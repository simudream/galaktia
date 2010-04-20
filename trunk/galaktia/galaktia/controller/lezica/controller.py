#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

# The Extendable Dispatcher Controller class is designed to allow a plugin-like
# behaviour of the Controllers. When the plug(foo) method is called, it scans
# the controller directory (as per import controllers.foo) for the module and
# loads it. Likewise, the unplug() method can be used to discontinue use of a
# specific Controller.

# Each Controller module (name).py should define the following:
#   - a (name)Controller class inherited from the Controller class, with:
#       - a MESSAGE_TYPE class variable with the message type the controller
#         intends to handle.
#       - a handle(message) method.

from abc import ABCMeta, abstractmethod

class ControllerImportError(Exception):
    """ Raised when a Controller Module is not found."""
    pass

class BadControllerError(Exception):
    """Raised when a Controller definition is bogus."""
    pass

class ControllerConflictError(Exception):
    """ Raised when a loading a Controller that attempts to handle a message
    type already handled by a previously loaded Controller. """

class Controller(object):
    """ Abstract Base Class for controllers """
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, message):
        """
        Handles a request message and yields reponse and notification
        messages.

        :return: iterable of ``Message`` instances
        """

class ExtendableDispatcherController(Controller):

    def __init__(self):
        self.routes = {}

    def plug(self, name, module = "controllers"):
        """
        Plugs a Controller, located in a (name).py file in the python import path.
        """
        
        try:
            _temp = __import__(module + '.' + name, 
                               fromlist = [name + 'Controller'])

            # [ERROR] the static/class variable MESSAGE_TYPE is NOT IMPORTED!
            _controller = getattr(_temp, name + 'Controller')
                        
        except ImportError:
            raise ControllerImportError # Why not use ImportError?

        # Is this validation that follows necessary? Better than an unhandled
        # error later on, I guess...

        if not (hasattr(_controller, 'MESSAGE_TYPE')
           and issubclass(_controller, Controller)):
            raise BadControllerError
        
        if _controller.MESSAGE_TYPE not in self.routes:
                self.routes[_controller.MESSAGE_TYPE] = _controller
        else:
            raise ControllerConflictError
            

    def unplug(self, name):
        """
        If the specified Controller is plugged, this method unplugs it from the EDC.
        """
        # WARNING: THIS METHOD IS NOT THREAD-SAFE
        #[TODO] Is this the correct way to do this? Doesn't look like so.

        try:
            for key in [k for k, v in self.routes.iteritems() if v.__name__ == name]:
                del self.routes[key]
        except:
            pass # or should we raise an exception?


    def handle(self, message):

        controller = self.__getRoute__(message)

        try:
            return controller.handle(message)

        except: # if controller fails...
            logger.exception('Failed to handle message: %s', message)
            return [] # TODO: send "internal server error" message


    def __getRoute__(self, message):
    
        try:
            return self.routes[message.type]
            
        except KeyError:
            logger.exception('Unknown message type: %s', message)
            
        except AttributeError:
            logger.exception('Bad message: %s', message)


if __name__ == "__main__":
    import sys
    EDC = ExtendableDispatcherController()
    EDC.plug(sys.argv[1])
    EDC.plug(sys.argv[1])  

    print EDC.routes

