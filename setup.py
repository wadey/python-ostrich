#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="ostrich",
      version="0.2",
      description="Python port of the Scala Ostrich library",
      author="Wade Simmons",
      author_email="wade@wades.im",
      url="http://github.com/wadey/python-ostrich",
      packages = find_packages(),
      license = "Apache 2.0",
      keywords="ostrich",
      zip_safe = True)
