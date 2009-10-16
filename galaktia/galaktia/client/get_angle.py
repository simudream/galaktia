import math

def get_angle(x, y):
    angle = math.atan(float(y)/float(x)) \
        if x != 0 else math.atan(float(y)/float(0.0001))
    if x > 0:
        if y > 0:
            # Cuadrante 1
            if math.pi/8 < angle < 3*math.pi/8:
                retval = 1
            elif angle >= 3*math.pi/8:
                retval = 0
            else:
                retval = 2
        elif y == 0:
            # Eje X
            retval = 2
        else:
            # Cuadrante 4
            if -math.pi/8 > angle > -3*math.pi/8:
                retval = 3
            elif angle <= -3*math.pi/8:
                retval = 4
            else:
                retval = 2
    elif x == 0:
        # Eje Y
        retval = 0 if y > 0 else 4
    else:
        if y > 0:
            # Cuadrante 2
            if -angle > 3*math.pi/8:
                retval = 0
            elif -angle < math.pi/8:
                retval = 6
            else:
                retval = 7
        elif y == 0:
            # Eje X
            retval = 6
        else:
            # Cuadrante 3
            if math.pi/8 < angle < 3*math.pi/8:
                retval = 5
            elif math.pi/8 >= angle:
                retval = 6
            else:
                retval = 4
    return retval
