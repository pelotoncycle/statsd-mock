#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='gevent-statsd-mock',
    version='0.0.1',
    description='statsd mock server based on gevent',
    author='Studio Ousia',
    author_email='admin@ousia.jp',
    url='http://github.com/studio-ousia/gevent-statsd-mock',
    packages=find_packages(),
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=['gevent', 'python-statsd'],
    tests_require=['nose']
)
