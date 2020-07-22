#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-flakefinder',
    version='0.1.3',
    author='David Euresti',
    author_email='david@euresti.com',
    maintainer='Nipunn Koorapati',
    maintainer_email='nipunn@dropbox.com',
    license='Apache',
    url='https://github.com/dropbox/pytest-flakefinder',
    description='Runs tests multiple times to expose flakiness.',
    long_description=read('README.rst'),
    py_modules=['pytest_flakefinder'],
    install_requires=['pytest>=2.7.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'pytest11': [
            'flakefinder = pytest_flakefinder',
        ],
    },
)
