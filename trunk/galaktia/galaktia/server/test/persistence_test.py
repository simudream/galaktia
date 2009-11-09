#!/usr/bin/env python
# -*- coding: utf-8 -*-


from unittest import TestCase, TestSuite, main
from galaktia.server.persistence.dao import SceneObjectDAO, SpatialDAO, \
         WallDAO, GroundDAO, UserDAO, ItemDAO, SpriteDAO, CharacterDAO, \
         CharacterItemDAO
from galaktia.server.persistence.orm import init_db, SceneObject, Wall, \
         Spatial, Ground, User, Item, Sprite, Character, CharacterItem


class daoTestCase(TestCase):
    """
        DAO test cases. Tests for bugs.
    """

    def setUp(self):
        """
            Setup of the testing environment. This function gets called every
            time a test method is run
        """
        database_uri='test_database.sqlite3'
        self.engine, self.metadata, self.Session = \
            init_db(db_connection_string="sqlite:///%s" % database_uri)
        self.session_instance = self.Session()


    def tearDown(self):
        self.session_instance.flush()
        self.session_instance.commit()
        self.session_instance.close()

    def test_map_creation(self):
        """ Tests the insertion of Wall objects """
        dao = WallDAO(self.session_instance)
        # Create a simple 10x10, layer 0 map:
        expected_result=[]
        for i,j in ((x,y) for x in range(10) for y in [0,9]):
            wall = Wall()
            wall.z = 0
            wall.x = i
            wall.y = j
            dao.add(wall)
            expected_result.append(wall)
        for i,j in ((x,y) for x in [0,9] for y in range(1,10)):
            wall.z = 0
            wall.x = i
            wall.y = j
            dao.add(wall)
            expected_result.append(wall)
        dao.session.flush()
        dao.session.commit()
        all_stationaries = dao.all()
        self.assertEqual(all_stationaries.sort(), expected_result.sort())
            # Assert the results.
        for i in all_stationaries:
            dao.delete(i)
            # Do cleanup.

    def test_character_dao(self):
        """ Can we create users? """
        walter = Character()
        walter.name = u'Walter'
        walterina = Character()
        walterina.name = u'Walterina'
        dao = CharacterDAO(self.session_instance)
        for i in dao.all():
            dao.delete(i)
        dao.add(walter)
        dao.add(walterina)
            # Add the chars to the database.
        #test delete, etc...

    def test_area_and_layer_querying(self):
        """ Create a minimap with some objects and test the get_layer_*
            methods
        """
        pass


