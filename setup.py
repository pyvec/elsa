# Encoding: UTF-8
#!/usr/bin/env python3
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 0):
    raise RuntimeError('Elsa needs Python 3 or greater')

setup(
    name='elsa',
    version='0.1.dev4',
    description='Helper module for Frozen-Flask based websites',
    long_description=''.join(open('README.rst').readlines()),
    keywords='flask web github',
    author='Miro Hrončok',
    author_email='miro@hroncok.cz',
    license='MIT',
    url='https://github.com/pyvec/elsa',
    packages=[p for p in find_packages() if p != 'tests'],
    install_requires=[
        'click',
        'Flask',
        'Frozen-Flask',
        'ghp-import',
        'sh',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        ]
)
