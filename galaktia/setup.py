#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='galaktia',
      version='0.1',
      description='A MMORPG game',
      author='Galaktia Team',
      author_email='contact@galaktia.com.ar',
      url='http://code.google.com/p/galaktia/',
      install_requires= [
        'pyglet',
        'twisted',
        'sqlalchemy',
        'simplejson',
      ],
      packages=find_packages(exclude=['ez_setup']),
     )

