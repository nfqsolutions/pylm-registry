#!/usr/bin/env python

from setuptools import setup

long_description = """
Pylm
====

Pylm is the Python implementation of PALM, a framework to build
clusters of high performance components. Pylm-registry provides
a set of tools to launch and monitor PALM clusters.

**Pylm requires a version of Python equal or higher than 3.4, and it is
more thoroughly tested with Python 3.5.**

Installing **pylm** is as easy as:

.. code-block:: bash

   $> pip install pylm-registry

* `PYPI package page <https://pypi.python.org/pypi/pylm-registry/>`_

* `Documentation <http://pylm-registry.readthedocs.io/en/latest/>`_

* `Source code <https://github.com/nfqsolutions/pylm-registry>`_

Pylm is released under a dual licensing scheme. The source is released
as-is under the the AGPL version 3 license, a copy of the license is
included with the source. If this license does not suit you,
you can purchase a commercial license from `NFQ Solutions
<http://nfqsolutions.com>`_

This project has been funded by the Spanish Ministry of Economy and
Competitivity under the grant IDI-20150936, cofinanced with FEDER
funds.
"""

setup(
    name='pylm-registry',
    description='Registry service to configure clusters of PALM components',
    long_description=long_description,
    version="0.4.11",
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
    install_requires=['pylm', 'tornado', 'sqlalchemy', 'cryptography'],
    setup_requires=['pytest-runner', 'pytest'],
    tests_require=['pytest'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['pylm-runner=pylm.registry.runner:main',
                            'pylm-registry=pylm.registry.application:main'],
    })

