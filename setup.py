try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='discos-simulators',
    version='1.0',
    description='Simulators for the DISCOS project',
    packages=find_packages(),
    scripts=['scripts/discos-simulator'],
    license='GPL',
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9.6',
    ],
)
