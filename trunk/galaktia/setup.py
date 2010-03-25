#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='galaktia',
      version='0.1',
      description='A MMORPG game',
      author='Galaktia Team',
      author_email='contact@galaktia.com.ar',
      url='http://code.google.com/p/galaktia/',
      install_requires=[
        'controlfreak>=1.0',
        'pycommons>=0.1',
        'PyYAML==3.08', # TODO: controlfreak dependence, deprecate
        'zope.interface==3.5.1', # TODO: controlfreak dependence, deprecate
        'pyglet>=1.1.3',
        'Twisted>=8.2',
        'SQLAlchemy>=0.5',
        'simplejson>=2.0',
        'pycrypto>=2.0',
        'mock>=0.5',
        'pymemtools>=0.1',  # TODO: Memory tools. Not used right now, but
                            # it was part of this project once.
      ],
      entry_points={
        'console_scripts': ['galaktia = galaktia.__init__:main']
      },
      packages=find_packages(exclude=['ez_setup']),
)
