# !/usr/bin/env python
# encoding: utf-8

from setuptools import find_packages, setup

NAME = 'phenome10k'
DESCRIPTION = 'Hosting of 3D biological models for the academic and educational community.'
URL = 'https://github.com/NaturalHistoryMuseum/phenome-10k'
EMAIL = 'phenome10k@nhm.ac.uk'
AUTHOR = 'Paul Kiddle, Ginger Butcher'
VERSION = '1.0.0'

with open('requirements.txt', 'r') as req_file:
    REQUIRED = [r.strip() for r in req_file.readlines()]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'p10k=api.phenome10k.cli:cli'
        ],
    },
    license='MIT'
    )
