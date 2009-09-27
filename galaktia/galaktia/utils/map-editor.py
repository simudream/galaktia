#!/usr/bin/env python

"""
Curses-based map editor for Galaktia
"""

# stdlib imports
from galaktia.server.persistence.orm import Wall, init_db
import optparse
import curses
import sys
import os

class LangParser(object):

    def __init__(self, Session,repres=None, verbosity=0):
        self.session = Session()
        self.repres = repres
        self.verbosity = verbosity
        if repres is None:
            self.repres = {
                "0" : Wall
            }
        self.repres[" "]=None
        self.repres["+"]=1
        self.repres["-"]=-1
        # Inverse representation: useful for dumping the map in a text file.
        # The encoder may be somewhat complex, and it's not so useful by now.
        self._inverse_repres = {}
        for key in self.repres:
            self._inverse_repres[self.repres[key]]=key

    def add_character(self, character, klass):
        pass

    def decode_and_store(self, text):
        x, y, z = 0, 0, 0
        obj = None
        lines = []
        if isinstance(text, file):
            lines = text.readlines()
        else:
            lines = text.splitlines()
        for line in lines:
            x = 0
            for character in line:
                try:
                    obj = self.repres[character]
                except KeyError:
                    obj = None
                if obj is None:
                    pass
                elif obj == 1:
                    x, y = 0, 0
                    z += 1
                elif obj == -1:
                    z -= 1
                    x, y = 0, 0
                else:
                    entity = obj()
                    entity.x = x
                    entity.y = y
                    entity.z = z
                    self.session.add(entity)
                    self.session.flush()
                    self.session.commit()
                    entity.name = unicode(type(entity)) + " " + \
                                  unicode(entity.id)
                    if self.verbosity == "1":
                        print >> sys.stdout, "%i\t%s\t%i\t%i\t%i" % \
                            (entity.id, entity.name, entity.x, entity.y, \
                             entity.z)
                    elif self.verbosity == "2":
                        print >> sys.stdout, \
                        """---\nID:\t%i\nName:\t%s\nX:\t%i\nY:\t%i\nZ:\t%i \
                        \n---
                        """ % (entity.id, entity.name, entity.x, \
                                    entity.y, entity.z)
                x += 1
            y += 1
        self.session.flush()
        self.session.commit()

class MapEditor(object):
    pass

class CursesMapEditor(MapEditor):
    def __init__(self):
        """
            Start the wrapper and the screen. Cast as singleton inside this
            app.
        """
        curses.wrapper(self._main)
        self.stdscr = None

    def _main(self, stdscr):
        """
            Run the app screen. Init'ing the class will only load the \
            wrapper.
        """
        self.stdscr = stdscr
        stdscr.addstr(0, 0, "TEST", curses.A_BOLD)
        stdscr.refresh()
        a=stdscr.getch()
        stdscr.addch(1,1,a)

def _init(connection_string, clear=False):
    eng, mdata, S = init_db(db_connection_string = connection_string)
    if clear:
        session = S()
        for i in session.query(Wall).all():
            session.delete(i)
        session.flush()
        session.commit()
    return S

def auto(options):
    load = options.load
    if options.load is None:
        load = sys.stdin
    Session = _init(options.dbase, options.clear)
    parser = LangParser(Session,verbosity=options.verb)
    parser.decode_and_store(load)


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-a", "--auto", action="store_true",
            dest="auto", default=False, help="fully automated.")
    parser.add_option("-d", "--database", action="store", dest="dbase",
            help="database URI to read and save the results." \
            " Defaults to ./dbase.sqlite.", default="sqlite:///dbase.sqlite")
    parser.add_option("-l", "--load", action="store", dest="load",
            help="matrix file to load contents from. Defaults to" \
            " stdin", default=None)
    parser.add_option("-v", "--verbosity", action="store", dest="verb",
            help="Sets the verbosity level. 0 for none (default), 1 for" \
            " one-line records and 2 for multiline.", default=0)
    parser.add_option("-n", "--no-gui", action="store_true", dest="ui",
            help = "Force Curses (console) interface", default=False)
    dangerous = optparse.OptionGroup(parser, "Dangerous Options")
    dangerous.add_option("-c", "--clear", action="store_true", dest="clear",
            help="clear ALL map entities.", default=False)
    dangerous.add_option("--run-as-root", action="store_true", dest="root",
            help="allow the map editor to run as root", default=False)
    parser.add_option_group(dangerous)
    (options, args) = parser.parse_args()
    if os.getuid() == 0 and options.root==False:
        print >> sys.stderr, "You must be out of your mind to run this as \
            root!"
        print >> sys.stderr, "Read the help!"
        if options.auto == True:
            sys.exit(1)
        else:
            print >> sys.stderr, "Are you SURE you want to do this anyway?"
            print >> sys.stderr, "Write 'Yes, I'm completely deranged'"
            if raw_input() != "Yes, I'm completely deranged":
                print >> sys.stderr, "Nice try, buddy..."
                sys.exit(1)

    if "...---..." in args:
        parser.print_help()
        sys.exit(0)
    if options.auto:
        auto(options)
    elif os.getenv('DISPLAY') is None or options.ui:
        cursesMapEditor = CursesMapEditor()
        print >> sys.stderr, ">> Insert a nice Curses interface here <<"
    else:
        print >> sys.stderr, ">> Insert GUI here <<"
