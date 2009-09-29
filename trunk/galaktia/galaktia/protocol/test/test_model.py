# -*- coding: utf-8 -*-
from __future__ import with_statement
__docformat__='restructuredtext'

import logging
import time

from unittest import TestCase

from galaktia.protocol.model import Message, Session, Datagram

# HOWTO install nose testing framework and run tests:
# $ easy_install nose
# $ nosetests -vs test_model.py

class TestMessage(TestCase):
    """ Unit test for `Message` model """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_empty_constructor(self):
        """ Does the Message constructor work as expected with no args? """
        now = time.time()
        msg = Message()
        self.assertTrue(msg.session is None)
        self.assertEqual(msg['name'], 'Message')
        self.assertTrue(msg['timestamp'] >= now)
        self.assertEqual(msg['ack'], [])
        self.assertEqual(set(msg.keys()), set(['name', 'timestamp', 'ack']))

    def test_constructor(self):
        """ Does the Message constructor work as expected with extra args? """
        now = time.time()
        session = Session()
        msg = Message(session=session, name='MockMessage', foo='bar', baz=1.2)
        self.assertEqual(msg.session, session)
        self.assertEqual(msg['name'], 'MockMessage')
        self.assertTrue(msg['timestamp'] >= now)
        self.assertEqual(msg['ack'], [])
        self.assertEqual(msg['foo'], 'bar')
        self.assertEqual(msg['baz'], 1.2)
        self.assertEqual(set(msg.keys()), \
                set(['name', 'timestamp', 'ack', 'foo', 'baz']))

    def test_dict(self):
        """ Does Message work as a dict? """
        session = Session()
        msg = Message(session=session)
        self.assertFalse('session' in dict(msg))
            # TODO: test that Message.session is not serialized
        self.assertEqual(msg['name'], 'Message')
        msg['foo'] = 'bar'
        self.assertEqual(msg['foo'], 'bar')
        msg['baz'] = 1.2
        self.assertEqual(msg['baz'], 1.2)
        self.assertEqual(set(msg.keys()), \
                set(['name', 'timestamp', 'ack', 'foo', 'baz']))
        del msg['foo']
        self.assertEqual(set(msg.keys()), \
                set(['name', 'timestamp', 'ack', 'baz']))

class TestDatagram(TestCase):
    """ Unit test for `Datagram` model """
    # TODO

class TestSession(TestCase):
    """ Unit test for `Session` model """
    # TODO

