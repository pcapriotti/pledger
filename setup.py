#!/usr/bin/env python

import os
import setuptools

APP_ROOT = os.path.dirname(__file__)
README = os.path.join(APP_ROOT, "README.md")
exec(open(os.path.join(APP_ROOT, "pledger", "_version.py")).read())

setuptools.setup(
    name="pledger",
    version=__version__,
    description="Command line accounting tool and library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com.com/pcapriotti/pledger",
    author="Paolo Capriotti",
    author_email="paolo@capriotti.io",
    license="MIT",
    packages=["pledger"],
    scripts=[
        "bin/pledger",
    ],
    python_requires=">= 3.7",
    install_requires=[],
)
