#!/usr/bin/env python
# -*- coding: utf-8 -*-


from unittest import TestCase, TestSuite, main
from galaktia.server.persistence.dao import SceneObjectDAO, SpatialDAO, \
         StationaryDAO, GroundDAO, UserDAO, ItemDAO, SpriteDAO, CharacterDAO, \
         CharacterItemDAO, PendingMessageDAO, SessionDAO
from galaktia.server.persistence.orm import init_db, SceneObject, Stationary, \
         Spatial, Ground, User, Item, Sprite, Character, CharacterItem, \
         PendingMessage, Session


class daoTestCase(TestCase):
    """
        DAO test cases. Tests for bugs.
    """

    def setUp(self):
        """
            Setup of the testing environment. This function gets called every
            time a test method is run
        """
        database_uri='../data/test_database.sqlite3'
        self.engine , self.metadata ,self.Session = \
            init_db(db_connection_string="sqlite:///%s" % database_uri)
        self.session_instance = self.Session()


    def tearDown(self):
        self.session_instance.flush()
        self.session_instance.commit()
        self.session_instance.close()

    def test_map_creation(self):
        """ Tests the insertion of Stationary objects """
        dao = StationaryDAO(self.session_instance)
        # Create a simple 10x10, layer 0 map:
        expected_result=[]
        for i,j in ((x,y) for x in range(10) for y in [0,9]):
            stationary = Stationary()
            stationary.z = 0
            stationary.x = i
            stationary.y = j
            dao.add(stationary)
            expected_result.append(stationary)
        for i,j in ((x,y) for x in [0,9] for y in range(1,10)):
            stationary.z = 0
            stationary.x = i
            stationary.y = j
            dao.add(stationary)
            expected_result.append(stationary)
        dao.session.flush()
        dao.session.commit()
        all_stationaries = dao.all()
        self.assertEqual(all_stationaries.sort(), expected_result.sort())
            # Assert the results.
        for i in all_stationaries:
            dao.delete(i)
            # Do cleanup.

    def test_character_to_character_collision(self):
        """ Create two crash test dummies to test collision.
        Poor Walter and Walterina! :'(
        """
        walter = Character()
        walter.name = u'Walter'
        walterina = Character()
        walterina.name = u'Walterina'
        dao = CharacterDAO(self.session_instance)
        for i in dao.all():
            dao.delete(i)
        dao.add(walter)
        dao.add(walterina)
        dao.session.flush()
        dao.session.commit()
            # Add the chars to the database.
        # ==== Single Layer Test ====
        dao.move(walter,1,1,0, warp=True)
        dao.move(walterina,2,2,0, warp=True)
        self.assertEqual(walter.pos(), (1, 1, 0))
        self.assertEqual(walterina.pos(), (2, 2, 0))
            # Move Walter and Walterina to their respective coords.
        self.assertEqual(dao.move(walter, 2, 2), True)
            # Move Walter to (2, 2, 0). Now both Walter and Walterina are in
            # the same cell.
        self.assertEqual(dao.move(walter, 2, 2), True)
            # Moving to the same place should always return True
        dao.move(walter, 1, 2, 0)
        self.assertEqual(dao.move(walter, 2, 2, 0), True)
            # It won't collide, since both objects are "ghosts"
        dao.move(walter, 1, 2, 0)
        self.assertEqual(dao.move(walter, 2, 2, 0), True)
            # Walterina is still a ghost
        walterina.collide=True
        dao.move(walter, 1, 2, 0)
        self.assertEqual(dao.move(walter, 2, 2, 0), False)
            # Now they will collide.
        self.assertEqual(dao.move(walter, 2, 2, 0, collide_objects=False), \
                True)
        dao.move(walter, 1, 2, 0)
        self.assertEqual(walter.pos(), (1, 2, 0))
            # Collide Walter with Walterina and see if Walter remains in 1-2-0
        # ==== Multi Layer Test ====
        self.assertEqual(dao.move(walter, 3, 3, 1, warp=True), True)
            # Move Walter to layer 1, x=3, y=3...
        self.assertEqual(dao.move(walter, 2, 2, 1), True)
            # ...and then move it to the same x-y where Walterina is. They
            # shouldn't collide.
        self.assertEqual(dao.move(walter, 2, 2, 0), False)
            # You can't step over Walterina! >:(
        walter.show=False
            # Now Walter is The Invisible Man!
        self.assertEqual(dao.move(walter, 2, 2, 0), False)
            # This will fail, since being invisible doesn't mean you can step
            # over people, they have to be invisible or collidable.
        walterina.show=False
        self.assertEqual(dao.move(walter, 2, 2, 0), True)
        walterina.show=True
        dao.move(walter, 2, 2, 1)
        self.assertEqual(walter.pos(), (2, 2, 1))
        self.assertEqual(dao.move(walter, 2, 2, 0), False)

    def test_area_and_layer_querying(self):
        """ Create a minimap with some objects and test the get_layer_*
            methods
        """
        pass

class persistenceTestSuite(TestSuite):
    pass


if __name__ == "__main__":
    main()
