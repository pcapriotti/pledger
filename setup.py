#!/usr/bin/env python

from setuptools import setup, find_packages
from pledger.version import VERSION

setup(name="pledger",
      version=".".join(str(x) for x in VERSION),
      description="Command line accounting tool and library",
      author="Paolo Capriotti",
      author_email="p.capriotti@gmail.com",
      url="https://github.com/pcapriotti/pledger",
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
          'console_scripts': [
              'plg = pledger.cli:run_cli' ] },
      license="MIT")
