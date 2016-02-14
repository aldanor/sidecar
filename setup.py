# -*- coding: utf-8 -*-

import io
import re
from setuptools import setup, find_packages

with io.open('src/sidecar/_version.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='sidecar',
    version=version,
    author='Ivan Smirnov',
    author_email='i.s.smirnov@gmail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'six',
        'tornado',
        'sockjs-tornado'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intented Audience :: Developers',
        'Framework :: Tornado',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Topic :: WWW/HTTP :: Dynamic Content'
    ]
)
