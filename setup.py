# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='sidecar',
    version='0.0.1',
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
