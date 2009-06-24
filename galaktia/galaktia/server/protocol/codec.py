#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson

from galaktia.server.protocol.model import Datagram, Message

class Codec(object):
    """ Encodes and decodes objects """

    def encode(self, decoded):
        raise NotImplementedError

    def decode(self, encoded):
        raise NotImplementedError

class SerializationCodec(Codec):
    """ Serializes and unserializes objects into a string representation.
        Objects can be compound as far as they consist of simple built-in
        types such as dict, list, tuple, str, unicode, int, float, etc. """

    def encode(self, decoded):
        return simplejson.dumps(decoded, separators=(',', ':'))

    def decode(self, encoded):
        return simplejson.loads(encoded)

class CompressionCodec(Codec):
    """ Compresses and decompresses strings via zlib """

    def encode(self, decoded):
        return decoded.encode('zlib')

    def decode(self, encoded):
        return encoded.decode('zlib')

class EncryptionCodec(Codec):
    """ Encrypts and decrypts strings with AES method """

    def encode(self, decoded):
        return decoded # TODO: encrypt the string with AES (pycrypto)

    def decode(self, encoded):
        return encoded # TODO: decrypt the string with AES (pycrypto)

class MultipleCodec(Codec):
    """ Applies multiple codecs iteratively """

    def __init__(self, codecs):
        self.codecs = tuple(codecs)

    def encode(self, decoded):
        for codec in codecs: # Functional programmers prefer foldr
            decoded = codec.encode(decoded)
        return decoded

    def decode(self, encoded):
        for codec in reversed(codecs): # Functional programmers prefer foldl
            encoded = codec.decode(encoded)
        return encoded

    # It would be so cool to concatenate a set of codecs using
    # MultipleCodec in order to implement an RPG game network protocol...
    # Unfortunately, there is coupling between the codecs we need,
    # so this elegant class turned out as impractical as a philosopher
    # playing football: http://www.youtube.com/watch?v=92vV3QGagck

class ProtocolCodec(Codec):
    """ Codec that converts Datagram to Message and viceversa.
        Designed for a multi-layer protocol that includes message
        serialization, compression and encryption. """

    def __init__(self, session_dao):
        self.session_dao = session_dao
        self.serializer = SerializationCodec()
        self.compressor = CompressionCodec()
        self.cipher = EncryptionCodec()

    def encode(self, decoded):
        host, port = decoded['host'], decoded['port']
        message = dict((k, v) for k, v in decoded.iteritems() \
                if k not in ('host', 'port'))
        serialized = self.serializer.encode(message)
        compressed = self.compressor.encode(serialized)
        password = self._get_password('%s:%s' % (host, port))
        encrypted = self.cipher.encode((compressed, password))[0]
        return Datagram(encrypted, host=host, port=port)

    def decode(self, encoded):
        encrypted, host, port = (encoded.data, encoded.host, encoded.port)
        password = self._get_password('%s:%d' % (host, port))
        decrypted = self.cipher.decode((encrypted, password))[0]
        decompressed = self.compressor.decode(decrypted)
        unserialized = self.serializer.decode(decompressed)
        return Message(host=host, port=port, **unserialized)

    def _get_password(self, session_id):
        session = self.session_dao.get(session_id)
        if session is None:
            raise ValueError # TODO: define InvalidSessionException
        return session.password

