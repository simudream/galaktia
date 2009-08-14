#!/usr/bin/env python
# -*- coding: utf-8 -*-

from galaktia.server.persistence.dao import StationaryDAO, CharacterDAO
from galaktia.server.persistence.orm import Stationary, Character, init_db
import sys
# This script generates the basic structure of the database, containing only
# Stationary entities.

# USAGE: the script reads from stdin the map matrix. 0 is a Stationary, while
# whitespace is used to mark free spots.

def parse(text):
    i, j, k = 0, 0, 0
    lines=[]
    objects=[]
    lines = text.splitlines()
    for line in lines:
        i = 0
        for char in line:
            if(char=="0"):
                stationary = Stationary()
                stationary.x=i
                stationary.y=j
                stationary.z=k
                objects.append(stationary)
            i += 1
            if (char=="-"):
                k +=1
                i=0
                j=0
                break
        j += 1
    return objects


if __name__=='__main__':
    print "running"
    regen=False
    text = sys.stdin.read()
    file = "map.sqlite3"
    print "reading from stdin"
    if "regen" in sys.argv:
        regen=True
    for i in sys.argv:
        if i != "regen" and i !=sys.argv[0] and i != sys.argv[1]:
            file=i
    print file
    a,b,c = init_db(db_connection_string="sqlite:///%s" % file)
    sdao = StationaryDAO(c)
    print text
    if regen:
        for i in sdao.all():
            sdao.delete(i)
    lista = parse(text)
    for each in lista:
        sdao.add(each)
        print "Adding <Stationary (",each.x, each.y, each.z,")> (that's j, i, k)"
    sdao.session.commit()
