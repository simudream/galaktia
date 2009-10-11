#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Provides utilities to generate encryption keys.

:date: '2009-09-25'
:authors:
    - jcivile
'''

import hashlib

class KeyGenerator(object):
    '''
    Generates keys for encryption & decription to be used by the protocol
    '''

    public_key = 'Llavepublicatroz'
    separator = ' - '

    @staticmethod
    def generate_key(session_id = 0, salt_list = None):
        
        '''
        Generates a new encryption key to use
        
        :parameters:
            session_id : int
                The session id attached to this key
            salt_list : tuple
                Extra data to salt the key with. It's *strongly* recommend to use a salt.
        '''
        
        if session_id == 0:
            return KeyGenerator.public_key
        
        hasher = hashlib.md5()
        hasher.update(str(session_id))
        
        if salt_list is not None:
            hasher.update(KeyGenerator.separator)
            for salt in salt_list:
                hasher.update(str(salt))
            
        return hasher.digest()