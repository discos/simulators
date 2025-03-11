#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='discos-simulators',
    version='1.1',
    description='Simulators for the DISCOS project',
    packages=find_packages(),
    scripts=['scripts/discos-simulator'],
    license='GPL',
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.13.2',
    ],
    include_package_data=True,
    package_data={
        'simulators': ['minor_servos/setup.csv']
    }
)
