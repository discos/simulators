try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='srtsim',
    version='0.1',
    description='Sardinia Radio Telescope simulators',
    packages=[
        'simulators',
    ],
    license='GPL',
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
   ],
)
