#!/usr/bin/env python

from setuptools import setup

setup(name='datatemplate',
      version='0.1',
      description='Renders various data sources via django templates',
      author='Joel Nothman',
      author_email='joel.nothman@gmail.com',
###      url='',
      packages=['datatemplate', 'datatemplate.template_libs', 'datatemplate.load_libs'],
      scripts=['scripts/datatemplate'],
      install_requires=['django'],
     )

