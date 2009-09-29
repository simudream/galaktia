#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys

import Image
import PngImagePlugin

class MetadataPNG(object):
    """ Model for a PNG image with the ability to read/write metadata """

    RESERVED = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')
    """ :cvar: PNG metadata reserved (read-only) keys """

    def __init__(self, filename):
        """ `MetadataPNG` constructor """
        self.filename = filename
        self._image = Image.open(filename)
        assert self._image.format == 'PNG', 'Not a PNG image: %s' % filename

    def __getitem__(self, key):
        """ Gets value for key as in a dict """
        return self._image.info[key]

    def __setitem__(self, key, value):
        """ Sets a key-value pair as in a dict """
        self._image.info[key] = value

    def __iter__(self):
        """ Metadata keys iterator """
        for i in self._image.info:
            yield i

    def update(self, items):
        """ Updates metadata with given key-value pairs """
        for k, v in dict(items).iteritems():
            self[k] = v

    def save(self, filename=None):
        """ Saves image as given or original filename """
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as stream:
            pnginfo = self._get_png_info()
            self._image.save(stream, 'PNG', pnginfo=pnginfo)

    def _get_png_info(self):
        """ Gets `PngImagePlugin.PngInfo` object (copy of current metadata) """
        # Adapted from code by Nick Galbreath
        # http://blog.modp.com/2007/08/python-pil-and-png-metadata-take-2.html
        pnginfo = PngImagePlugin.PngInfo()
        for k, v in self._image.info.iteritems():
            if k not in self.RESERVED:
                pnginfo.add_text(k, v, 0)
        return pnginfo

def test_metadata_png(filename, metadata=None):
    """
    Tests `MetadataPNG` read/write. Prints resulting key-value pairs.

    :parameters:
        filename : str
            PNG image filename
        metadata : str (optional)
            Key-value pairs to write (serialized, separated by ',' and ':')
    """
    png = MetadataPNG(filename)
    # write new metadata (key-value pairs separated by ',' and ':')
    if metadata is not None:
        png.update(tuple(i.strip() for i in i.split(':', 1)) \
                for i in metadata.split(','))
        png.save()
    # read metadata (and print via stdout)
    print '\n'.join('%s\t%s' % (i, png[i]) for i in png)

def main(program, filename=None, metadata=None, *args):
    """ Main program (command line arguments validation) """
    if filename is None:
        print 'usage: python %s [PNG image filename]' % program
    elif len(args) > 0:
        print 'unexpected arguments: ' + ' '.join(args)
    else:
        test_metadata_png(filename, metadata) # test PNG metadata read/write

if __name__ == '__main__':
    main(*sys.argv)

