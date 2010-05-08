#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='galaktia',
      version='0.2.0',
      description='A MMORPG game',
      author='Galaktia Team',
      author_email='contact@galaktia.com.ar',
      url='http://code.google.com/p/galaktia/',
      install_requires=[
        'controlfreak>=1.1.3, <1.2',
        'SQLAlchemy>=0.6',
        'mod_pywebsocket>=0.5', # FIXME
        #'pycrypto>=2.0', # deprecated? pyOpenSSL
      ],
      setup_requires=[
        'nose>=0.11',
        'pmock>=0.3',
      ],
      test_suite='nose.collector',
      entry_points={
        'console_scripts': ['galaktia = galaktia.__init__:main']
      },
      packages=find_packages(exclude=['ez_setup']),
)
