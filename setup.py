try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

additional_packages = [
    'numpy',
    'scipy',
]

extras = {
    'test': additional_packages,
}

setup(
    name='discos-simulators',
    version='0.1',
    description='Simulators for the DISCOS project',
    packages=find_packages(),
    scripts=['scripts/discos-simulator'],
    license='GPL',
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=additional_packages,
    tests_require=additional_packages,
    extras_require=extras,
)
