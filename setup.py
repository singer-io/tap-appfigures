#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-appfigures',
      version='0.0.1',
      description='Singer.io tap for extracting data from the AppFigures API',
      author='coen@compassmentis.com for Meow Wolf',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_appfigures'],
      install_requires=[
          'singer-python==5.5.1',
          'requests==2.20.1',
          'python-dateutil',
          'pytz',
      ],
      entry_points='''
          [console_scripts]
          tap-appfigures=tap_appfigures:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_appfigures': [
              'schemas/*.json'
          ]
      })
