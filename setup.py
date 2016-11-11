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

install_requires = []

setup(
    name='pyparxe',
    version=__version__,
    packages=[str('parxe')],
    ext_modules=[],
    install_requires=install_requires,
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
    test_suite="parxe.tests",
)
