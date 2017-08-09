try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='discos-simulators',
    version='0.1',
    description='Simulators for the DISCOS project',
    packages=['simulators'],
    scripts=['scripts/discos-simulator'],
    license='GPL',
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
   ],
)
