#!/usr/bin/env python

from setuptools import setup

setup(name='datatemplate',
      version='0.2',
      description='Renders various data sources via Django templates',
      author='Joel Nothman',
      author_email='joel.nothman@gmail.com',
      url='https://github.com/jnothman/datatemplate',
      packages=['datatemplate', 'datatemplate.template_libs', 'datatemplate.load_libs'],
      scripts=['scripts/datatemplate'],
      install_requires=['django'],
      license='Apache 2.0',
     )

