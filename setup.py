#!/usr/bin/env python3

from jira import __version__ as VERSION

from setuptools import setup

setup(
    name='jira-cli',
    description='a jira console client',
    version=VERSION,
    packages=['jira'],
    author='Simon Poirier',
    author_email='simpoir@gmail.com',
)
