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
    license='Apache',
    url='https://github.com/aldanor/sidecar',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'six',
        'tornado',
        'sockjs-tornado'
    ],
    include_package_data=True,
    package_data={'': [
        'static/*.css',
        'static/*.js',
        'static/*.html',
        'static/fonts/*.css',
        'static/fonts/*.woff'
    ]},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intented Audience :: Developers',
        'Framework :: Tornado',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent',
        'Topic :: WWW/HTTP :: Dynamic Content'
    ]
)
