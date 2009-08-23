#!/usr/bin/env python

"""
Curses-based map editor for Galaktia
"""

# stdlib imports
import optparse
import curses
import sys

class LangParser(object):
    def __init__(self, error_report=1):
        pass

class MapEditor(object):
    pass

def auto(stdin):
    pass

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-a", "--auto", action="store_true",
            dest="auto", default=False, help="Read from stdin.")
    parser.add_option("-f", "--file", action="store", dest="file",
            help="file to read and save the results")
    parser.add_option("-l", "--load", action="store", dest="load",
            help="file to load contents from")
    parser.add_option("-m", "--your-mom", action="count",
            dest="yourmom", default=False, help="Tell a 'your mom' joke")
    parser.add_option("-v", "--verbosity", action="store", dest="verb",
            help="Sets the verbosity level. 0 for none (default), 1 for" \
            " one-line records and 2 for multiline.", default=0)
    dangerous = optparse.OptionGroup(parser, "Dangerous Options")
    dangerous.add_option("-c", "--clear", action="store_true", dest="clear",
            help="Clear ALL map entities.", default=False)
    parser.add_option_group(dangerous)
    (options, args) = parser.parse_args()
    if "...---..." in args:
        parser.print_help()
        sys.exit(0)
    print options
    print args
