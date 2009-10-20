# -*- coding: utf-8 -*-

def cross( (x1,y1) , (x2,y2) ):
	return x1*y2 - x2*y1

def get_angle(x, y):
	P = ( (-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2) )
	for i in range(0,8):
		if( cross( P[i], (x,y) ) < 0 and cross( (x,y) , P[i+1] ) <= 0 ):
			return i
		return 'X'