'''
Created on Oct 17, 2009

@author: champo
'''

from galaktia.server.persistence.dao import WallDAO, CharacterDAO, \
        UserDAO

class DAOResolver(object):
    '''
    Resolves and keeps instances of DAO classes
    '''


    def __init__(self, db_session):
        '''
        Instance DAOResolver
        
        : parameters :
            db_session : object
                The database session
        '''
        
        self.db = db_session
        
        self.user = UserDAO(self.db())
        self.char = CharacterDAO(self.db())
        self.wall = WallDAO(self.db())
        
        
        