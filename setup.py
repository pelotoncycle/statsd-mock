#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='statsdmock',
    version='0.0.1',
    description='statsd mock server based on gevent',
    author='Salton Massally',
    author_email='salton.massally@gmail.com',
    url='http://github.com/tarzan0820/mock-statsd',
    packages=find_packages(),
    license=open('LICENSE.txt').read(),
    include_package_data=True,
    install_requires=['gevent', 'statsd'],
    tests_require=['nose'],
    test_suite='nose.collector',
    keywords = ['testing', 'logging'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
