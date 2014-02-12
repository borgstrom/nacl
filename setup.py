#!/usr/bin/env python

from setuptools import setup

import re

# load our version from our init file
init_data = open('naci/__init__.py').read()
matches = re.search(r"__version__ = '([^']+)'", init_data, re.M)
if matches:
    version = matches.group(1)
else:
    raise RuntimeError("Unable to load version")

setup(
    name='naci',
    packages=['naci'],
    include_package_data=True,
    version=version,
    license="TODO",
    description='A pure Python interface for generating SaltStack state data',
    long_description=open('README.rst').read(),
    author='Evan Borgstrom',
    author_email='evan@borgstrom.ca',
    url='https://github.com/borgstrom/naci',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        #'License :: OSI Approved :: TODO',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['salt']
)
