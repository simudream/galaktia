#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import struct

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
    
    def __init__(self, session_dao):
        self._session_dao = session_dao

    def encode(self, decoded):
        #TODO: Document that this method recieves a tuple with (data, session_id)
        return decoded[0] # TODO: encrypt the string with AES (pycrypto)

    def decode(self, encoded):
        #TODO: Document that this method recieves a tuple with (data, session_id)
        return encoded[0] # TODO: decrypt the string with AES (pycrypto)

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

class ProtocolCodec(MultipleCodec):
    """ Codec that converts Datagram to Message and viceversa.
        Designed for a multi-layer protocol that includes message
        serialization, compression and encryption. """

    _packer = struct.Struct( '!l' )

    def __init__(self, session_dao):
        self._session_dao = session_dao
        
        self._serializer = SerializationCodec()
        self._cypher = EncryptionCodec(session_dao)
        self._compresser = CompressionCodec()

    def encode(self, decoded):
        data = self._serializer.encode(decoded)
        data = self._cypher.encode((data, decoded.session))
        data = self._packer.pack( decoded.session ) + data
        data = self._compresser.encode(data)
        
        return Datagram(data, host=decoded.host, port=decoded.port)

    def decode(self, encoded):
        data = self._compresser.decode(encoded.data)
        data, session = data[self._packer.size:], \
            self._packer.unpack(data[:self._packer.size])[0]
        data = self._cypher.decode((data, session))
        data = self._serializer.decode(data)
        
        return Message(host=encoded.host, port=encoded.port, session=session,
                       **dict((str(k), v) for k, v in data.iteritems()))

