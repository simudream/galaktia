#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit-testing module for protocol.codec 

:date: '2009-08-14'
:authors:
    - Champo
"""

import unittest
from zlib import error

from mock import Mock

from galaktia.protocol.codec import SerializationCodec, CompressionCodec, EncryptionCodec, IdentifierPackerCodec, ProtocolCodec
from galaktia.protocol.key import KeyGenerator
from galaktia.protocol.model import Message
from galaktia.protocol.model import SessionDAO, Session

class TestSerializationCodec(unittest.TestCase):

    def setUp(self):
        self.codec = SerializationCodec()
        
        self.decoded = { 'foo': 'bar', 'morefoo': [ 'bar', 'foo' ] }
        self.encoded = '{"foo":"bar","morefoo":["bar","foo"]}'

    def tearDown(self):
        pass

    def test_encode(self):
        """ Can it serialize? """
        self.assertEqual(self.codec.encode(self.decoded), self.encoded)
        
    def test_encode_empty_dict(self):
        """ Can it serialize an empty dict? """
        self.assertEqual(self.codec.encode(dict()), '{}')
        
    def test_encode_none(self):
        """ Can it serialize nothing? """
        self.assertEqual(self.codec.encode(None), 'null')
        
    def test_decode(self):
        """ Can it unserialize? """
        self.assertEqual(self.codec.decode(self.encoded), self.decoded)
        
    def test_decode_object(self):
        """ Does it raise an error when an object is unserialized? """
        self.assertRaises(TypeError, self.codec.decode, Mock())
        
    def test_decode_invalid(self):
        """ Does it raise an error when a invalid string is unserialized? """
        self.assertRaises(ValueError, self.codec.decode, '{"}')
        
    def test_codec(self):
        """ Test the serialization-unserialization process """
        
        value = '42 is a nice number that you can take home and introduce to your family'
        
        self.assertEqual(self.codec.decode(self.codec.encode({'value':value})), {'value':value})
    
class TestCompressionCodec(unittest.TestCase):
    
    def setUp(self):
        self.codec = CompressionCodec()
        
        self.decoded = 'compression test string'
        self.encoded = 'x\x9cK\xce\xcf-(J-.\xce\xcc\xcfS(I-.Q(.)\xca\xccK\x07\x00p\x9e\tJ'
    
    def tearDown(self):
        pass
    
    def test_encode(self):
        """ Can it compress a simple string? """
        self.assertEqual(self.codec.encode(self.decoded), self.encoded)
    
    def test_encode_object(self):
        """ Does it raise an error when it tries to compress an object? """        
        self.assertRaises(Exception, self.codec.encode, Mock())
        
    def test_encode_none(self):
        """ Does it raise an error when it tries to compress None? """        
        self.assertRaises(AttributeError, self.codec.encode, None)

    def test_encode_failure(self):
        """ Is the compression of two different strings different? """
        self.assertNotEqual(self.codec.encode(self.decoded + 'foobar'), self.encoded)
    
    def test_decode(self):
        """ Can it decompress a simple string? """
        self.assertEqual(self.codec.decode(self.encoded), self.decoded)
        
    def test_decode_corrupt(self):
        """ Does it raise an error when a corrupt string is decompressed? """
        corrupt = self.encoded[1:]
        self.assertRaises(ValueError, self.codec.decode, corrupt)
        
    def test_decode_object(self):
        """ Does it raise an error when trying to decode an decompressed? """
        self.assertRaises(Exception, self.codec.decode, Mock())
        
    def test_decode_none(self):
        """ Does it raise an error when trying to decompress None? """
        self.assertRaises(AttributeError, self.codec.decode, None)
        
    def test_codec(self):
        """ Test the compression-decompression process """
        
        value = 'Flying is learning how to throw yourself at the ground and miss.'
        
        self.assertEqual(self.codec.decode(self.codec.encode(value)), value)
    
class TestEncryptionCodec(unittest.TestCase):
    
    def setUp(self):
        self.codec = EncryptionCodec()
        self.key = 'Aqueleyoyomamaci'
        self.encoded = ''
        self.decode = ''
    
    def tearDown(self):
        pass
        
    def test_decode(self):
        """ Can it decrypt a simple string? """
        self.assertEqual(self.codec.decode((self.encoded, self.key)), (self.decode, self.key))
     
    def test_decode_equal(self):
        """ Is the decrypted result of the same input equal? """        
        self.assertEqual(self.codec.decode(('some-random-message', self.key)), 
                         self.codec.decode(('some-random-message', self.key)))
    
    def test_decode_empty(self):
        """ Is the decrypted result of an empty input empty? """
        self.assertEqual(self.codec.decode(('', self.key)), ('', self.key))                        
    
    def test_decode_object(self):
        """ Does it raise an error when trying to decrypt an object? """
        self.assertRaises(Exception, self.codec.decode, (Mock(), self.key))
    
    def test_encode(self):
        """ Can it encrypt a simple string? """
        self.assertEqual(self.codec.encode((self.decode, self.key)), (self.encoded, self.key))
        
    def test_encode_empty(self):
        """ Can it encrypt an empty string? """
        self.assertEqual(self.codec.encode(('', self.key)), ('', self.key))
    
    def test_encode_object(self):
        """ Does it raise an error when trying to encrypt an object? """
        self.assertRaises(Exception, self.codec.encode, (Mock(), self.key))
        
    def test_encode_equal(self):
        """ Is the result of encrypting the same input equal? """
        self.assertEqual(self.codec.encode(('some-random-message', self.key)), 
                         self.codec.encode(('some-random-message', self.key)))
        
    def test_codec(self):
        """ Test the encrypting-decrypting process """
        
        # DO NOT Alter the strings
        
        value = 'The major difference between a thing that might go wrong and a' \
            ' thing that cannot possibly go wrong is that when a thing that' \
            ' cannot possibly go wrong goes wrong it usually turns out to be' \
            ' impossible to get at or repair.     '
        
        self.assertEqual(self.codec.decode(self.codec.encode((value, self.key))), (value, self.key))
    
class TestIdentifierPackerCodec(unittest.TestCase):
    
    def setUp(self):
        self.codec = IdentifierPackerCodec()
        
        self.encoded = '\x00\x00\x00 I dont mind'
        self.decoded = (32, 'I dont mind')
    
    def tearDown(self):
        pass
        
    def test_encode(self):
        """ Can it pack? """
        self.assertEqual(self.codec.encode(self.decoded), self.encoded)
    
    def test_encode_empty(self):
        """ Can it pack an empty string? """
        self.assertEqual(self.codec.encode((32, '')), '\x00\x00\x00 ')
    
    def test_encode_equal(self):
        """ Is the packing of the same input equal? """
        self.assertEqual(self.codec.encode(self.decoded), self.codec.encode(self.decoded))
        
    def test_encode_different_id(self):
        """ Is the packing of different input different? """
        self.assertNotEqual(self.codec.encode((32, '')),self.codec.encode((100, '')))
        
    def test_decode(self):
        """ Can it unpack? """
        self.assertEqual(self.codec.decode(self.encoded), self.decoded)
        
    def test_decode_empty(self):
        """ Does it raise an error when unpacking an empty string? """
        self.assertRaises(Exception, self.codec.decode, '')
        
    def test_decode_equal(self):
        """ Is the unpacking of the same input equal? """
        self.assertEqual(self.codec.decode(self.encoded), self.codec.decode(self.encoded))
        
    def test_decode_different(self):
        """ Is the unpacking of different input different? """
        self.assertNotEqual(self.codec.decode('\x00\x00\x00 '),self.codec.decode('\x00\x00\x00\x00'))
            
    def test_codec(self):
        """ Test the packing-unpacking process """
        
        data = 'In the beginning the universe was created. This made a lot of'\
            ' people angry and has been widely regarded as a "bad move"'
        
        id = 42 # You had to see this one coming
        
        self.assertEqual(self.codec.decode(self.codec.encode((id, data))), (id, data))
    
class TestProtocolCodec(unittest.TestCase):
    
    def setUp(self):
        self.codec = ProtocolCodec(self.session_dao)
    
    def tearDown(self):
        pass
        
    def test_encode(self):
        """ Can it encode? """
        self.assertTrue(False)
        
    def test_encode_equal(self):
        """ Is the encoding of the same input equal? """
        self.assertTrue(False)
        
    def test_encode_different(self):
        """ Is the encoding of different input different? """
        self.assertTrue(False)
        
    def test_encode_without_session(self):
        """ Does it raise an error when encoding without a session? """
        self.assertTrue(False)
            
    def test_decode(self):
        """ Can it decode? """
        self.assertTrue(False)
        
    def test_decode_without_session(self):
        """ Can it decode a sessionless datagram? """
        self.assertTrue(False)
        
    def test_decode_with_invalid_key(self):
        """ Does it raise an error when decoding with an invalid key? """
        self.assertTrue(False)
        
    def test_decode_equal(self):
        """ Is the decoding of the same input equal? """
        self.assertTrue(False)
        
    def test_codec(self):
        """ Test the encoding-decoding process """
        self.assertTrue(False)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()