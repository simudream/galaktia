#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='galaktia',
      version='0.1',
      description='A MMORPG game',
      author='Galaktia Team',
      author_email='contact@galaktia.com.ar',
      url='http://code.google.com/p/galaktia/',
      install_requires= [
        'pyglet>=1.1',
        'Twisted>=8.2',
        'SQLAlchemy>=0.5',
        'simplejson>=2.0',
        'pycrypto>=2.0',
        'mock>=0.5',
      ],
      packages=find_packages(exclude=['ez_setup']),
     )

