#!/usr/bin/env python

from setuptools import setup

setup(
    name='palm-registry',
    description='Registry service to configure clusters of PALM components',
    version="0.1",
    author="See AUTHORS file",
    author_email="solutions@nfq.es",
    packages=[
        pylm.registry
        ],
    namespace_packages=['pylm'],
    install_requires=['pylm', 'tornado'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'])

    
