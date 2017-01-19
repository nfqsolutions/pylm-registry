#!/usr/bin/env python

from setuptools import setup

setup(
    name='pylm-registry',
    description='Registry service to configure clusters of PALM components',
    version="0.3.1",
    author="See AUTHORS file",
    author_email="solutions@nfq.es",
    packages=[
        'pylm.registry',
        'pylm.registry.templates',
        'pylm.registry.static',
        'pylm.registry.clients',
        'pylm.registry.handlers',
        'pylm.registry.handlers.persistency'
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
    entry_points={
        'console_scripts': ['pylm-runner=pylm.registry.runner:main',
                            'pylm-registry=pylm.registry.application:main'],
    })

