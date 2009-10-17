from time import time
from galaktia.server.persistence.dao import CharacterDAO, SpatialDAO, WallDAO
from galaktia.server.persistence.orm import Character, Spatial, Sprite, Wall

class PositionalEngine(object):
    """
        The Positional system engine, responsible of moving objects in the
        World.
    """

    __map = {
        (0,1): 0,
        (1,1): 1,
        (1,0): 2,
        (1,-1): 3,
        (0,-1): 4,
        (-1,-1): 5,
        (-1,0): 6,
        (-1,1): 7
    }

    def __init__(self, Session, collide=True):
        """
            @params:
            Database Session class
        """
        self.Session = Session
        self.spatialDao = SpatialDAO(Session())
        self.wallDao = WallDAO(Session())
        self.charDao = CharacterDAO(Session())
        self.collide = collide
        self.distance = 1

    def __sign(self, n):
        return (0 if n == 0 else n/abs(n))

    def _raw_distance(self, *args):
        """ Returns the norm of the vector """
        return float((sum([x**2 for x in args]))**0.5)

    def _walktime(self, object):
        return abs(object.arrival_timestamp - time())

    def is_valid_speed(self, obj, x, y):
        """ Returns False if the object has exceeded its speed, otherwise
            True. This function makes use of _walktime, which compares the
            object's arrival_timestamp against time.time()
        """
        if self._raw_distance(obj.x-x, obj.y-y)/self._walktime(obj) > \
                obj.speed:
            return False
        else:
            return True

    def is_valid_distance(self, obj, x, y):
        if abs(obj.x-x) > self.distance or abs(obj.y-y) > self.distance:
            return False
        else:
            return True

    def _obstacles(self, obj, x, y, z):
        spatials = self.spatialDao.get_by_coords(x, y, z)
        if (not self.collide and not obj.collide):
            characters = [char for char in self.charDao.get_by_coords(x, y, z)
            if char.collide and char != obj]
            spatials = [a for a in spatials if a not in characters]
        if spatials:
            return True
        return False

    def move_3D(self, obj, x, y, z):
        if not self.is_valid_distance(obj, x, y) or \
            not self.is_valid_speed(obj, x, y):
            return False
        # Get the objects in the path where the user wants to move:
        if not self._obstacles(obj, x, y, z):
            # if no objects are found in the position I want to move to..
            obj.x = x
            obj.y = y
            obj.z = z
            obj.arrival_timestamp = time()
            return True
        else:
            return False
        return True

    def move(self, obj, x, y):
        self.move_3D(obj, x, y, obj.z)

    def warp_3D(self, obj, x, y, z):
        """
            Warps to a valid obstacle zone or returns False
        """
        walls = self.wallDao.get_by_coords(x, y, z)
        if not walls:
            obj.x = x
            obj.y = y
            obj.z = z
            obj.arrival_timestamp = time()
            return True
        return False

    def warp(self, obj, x, y):
        self.warp_3D(obj, x, y, obj.z)

    def dx_dy_look(self, obj, dx, dy):
        try:
            obj.direction = self.__map[(dx, dy)]
        except:
            if dx != 0 or dy != 0:
                self.dx_dy_look(self, self.__sign(dx), self.__sign(dy))

    def d_move(self, obj, (dx, dy)):
        """
            Moves the char using dx dy positioning. Returns False if the
            character cannot move to any position, or the effective \
            (dx,dy) otherwise.

            The next ASCII illustration shows how orientation, diferential
            and projection views are related.

            7    0    1        (-1,1)  (0,1)  (1,1)             (1,1)
                 o                       o
            6   /|\   2  --->  (-1,0)   /|\   (1,0)  --->  (-1,1)   (1,-1)
             ___/_\___               ___/_\___
            5    4    3        (-1,-1) (0,-1) (1,-1)           (-1,-1)

            If the user wants to go to (1, -1) and finds a wall, then the
            character will be moved to (0,-1), and if it cannot move there,
            then it will try (1,0). In a more general way: if
            dx*dy != 0 and if (dx, dy) is not valid, then try to move
            horizontally and then vertically.

            This function has been designed to emulate the legacy movement
            system.
        """
        if dx == 0 and dy == 0:
            return (0, 0)
        # Check speed:
        if 1.0/abs(obj.arrival_timestamp - time()) > obj.speed:
            return False
        for x, y in [(dx, dy), (dx, 0), (0, dy)]:
            if not self._obstacles(obj, obj.x+x, obj.y+y, obj.z):
                obj.x += x
                obj.y += y
                obj.arrival_timestamp = time()
                self.dx_dy_look(obj, x, y)
                return (x, y)
        return False
