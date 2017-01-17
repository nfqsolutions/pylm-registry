#!/usr/bin/env python

from setuptools import setup

setup(
    name='pylm-registry',
    description='Registry service to configure clusters of PALM components',
    version="0.1.7",
    author="See AUTHORS file",
    author_email="solutions@nfq.es",
    packages=[
        'pylm.registry'
        ],
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Operating System :: POSIX',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6'],
    namespace_packages=['pylm'],
    install_requires=['pylm', 'tornado', 'sqlalchemy'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
    scripts=['scripts/pylm-registry'])

