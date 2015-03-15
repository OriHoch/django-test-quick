#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-test-quick',
    version='1.0.0',
    author='Ori Hoch',
    author_email='ori@uumpa.com',
    description='django management command to allow quicker running of tests',
)
