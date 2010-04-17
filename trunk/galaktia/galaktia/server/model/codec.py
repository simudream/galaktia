#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Codecs are objects able to transform objects of some type into objects
of some other type (encode) and viceversa (decode).
"""

import json

class Codec(object):
    """ Encodes and decodes objects """

    def encode(self, decoded):
        raise NotImplementedError('abstract method')

    def decode(self, encoded):
        raise NotImplementedError('abstract method')

class JsonCodec(object):

    def encode(self, decoded):
        return json.dumps(decoded, default=self._encode)

    def _encode(self, unserializable):
        d = dict((attr, getattr(unserializable, attr)) for attr in \
                dir(unserializable) if not attr.startswith('_'))
        d['__class__'] = unserializable.__class__.__name__
        return d

    def decode(self, encoded):
        return json.loads(encoded, object_hook=self._decode)

    def _decode(self, decoded):
        klass = decoded.get('__class__')
        if klass:
            del decoded['__class__']
            decoded = eval(klass)(**decoded) # TODO: is eval efficient?
        return decoded

