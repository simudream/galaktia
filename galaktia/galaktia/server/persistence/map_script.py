#!/usr/bin/env python
# -*- coding: utf-8 -*-

from galaktia.server.persistence.dao import StationaryDAO
from galaktia.server.persistence.orm import Stationary, init_db
import sys
# This script generates the basic structure of the database, containing only
# Stationary entities.

def parse(text):
    i, j, k = 0, 0, 0
    lines=[]
    objects=[]
    if(isinstance(text, file)):
        lines = text.readlines()
    elif(isinstance(text, str)):
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
                break
        j += 1
    return objects


if __name__=='__main__':
    print "running"
    if(len(sys.argv)<2):
        text = sys.stdin.read()
        print "reading from stdin"
    else:
        text = open(sys.argv[2])
        print "reading from file"
    a,b,c = init_db(db_connection_string="sqlite:///map.sqlite3")
    sdao = StationaryDAO(c)
    print text
    lista = parse(text)
    for each in lista:
        sdao.add(each)
        print "Adding <Stationary (",each.x, each.y, each.z,")>"
    sdao.session.commit()
