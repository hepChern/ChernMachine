from distutils import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

PACKAGE = "ChernMachine"
NAME = "Chern Machine"
DESCRIPTION = "The running machine for Chern toolkit"
AUTHOR = "Mingrui Zhao"
AUTHOR_EMAIL = "mingrui.zhao@mail.labz0.org"
URL = "https://github.com/hepChern/ChernMachine"
VERSION = __import__(PACKAGE).__version__
here = os.path.dirname(__file__)
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url = URL,
    classifiers = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',

    ],
    zip_safe=False,
    keywords = "Analysis Perservation",
    packages = find_packages(exclude=[]),
    install_requires = [
        "Chern==3", "click", "colored", "python-daemon", "ipython"
    ],
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'chern_machine = ChernMachine.main:main',
            'chen_mahine = ChernMachine.main:main'
        ]
    }
)
