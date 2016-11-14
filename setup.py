# -*- coding: utf-8 -*-
import os
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup, Extension
from distutils.core import Extension
from distutils.errors import DistutilsError
from distutils.command.build_ext import build_ext

with open(os.path.join('parxe','__init__.py')) as f:
    exec(f.read())

tests_require = ['nose', 'nanomsg']
install_requires = ['nanomsg']
setup_requires = ['nanomsg']

setup(
    name='pyparxe',
    version=__version__,
    packages=[str('parxe')],
    ext_modules=[],
    tests_require=tests_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    description='PARallel eXecution Engine for Python.',
    classifiers=[
        "Development Status :: 0 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    author=__author__,
    author_email=__email__,
    url='https://github.com/pakozm/pyparxe',
    keywords=['pyparxe'],
    license=__license__,
    test_suite="nose.collector",
)
