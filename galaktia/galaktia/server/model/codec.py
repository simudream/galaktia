#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Codecs are objects able to convert objects of some type into objects
of some other type (encode) and viceversa (decode).
"""

from abc import ABCMeta, abstractmethod
import json

class Codec(object):
    """ Encodes and decodes objects """
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self, decoded):
        """ Encodes object of decoded type into another of encoded type """

    @abstractmethod
    def decode(self, encoded):
        """ Decodes object of encoded type into another of decoded type """

class ObjectPathCodec(Codec):
    """ Converts an object into its path string and viceversa """

    def decode(self, path):
        if ':' in path:
            module_path, attrs = path.split(':', 1)
            obj = __import__(module_path, fromlist=['__name__'])
            for attr in attrs.split('.'):
                obj = getattr(obj, attr)
            obj = obj() # fails if object constructor requires args
        else: # raw module path (not an object)
            obj = __import__(path, fromlist=['__name__'])
        return obj

    def encode(self, obj):
        klass = obj.__class__
        return ':'.join([klass.__module__, klass.__name__])

class JsonCodec(Codec):
    """ Converts objects into JSON strings and viceversa """

    # NOTE: This JSON codec is able to encode/decode objects
    # of any class whose constructor requires no arguments

    object_path_codec = ObjectPathCodec()

    def encode(self, decoded):
        return json.dumps(decoded, default=self._encode)

    def _encode(self, unserializable):
        serializable = dict((attr, getattr(unserializable, attr)) for attr in \
                dir(unserializable) if not attr.startswith('_'))
        path = self.object_path_codec.encode(unserializable)
        serializable['__class__'] = path
        return serializable

    def decode(self, encoded):
        return json.loads(encoded, object_hook=self._decode)

    def _decode(self, decoded):
        path = decoded.get('__class__')
        if path is not None:
            del decoded['__class__']
            obj = self.object_path_codec.decode(path)
            for k, v in decoded.iteritems():
                setattr(obj, k, v)
            decoded = obj
        return decoded

