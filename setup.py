#!/usr/bin/env python
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from bc_events/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("bc_events", "__init__.py")


def get_requirements(*file_paths):
    """Retrieves the requirements from a requirements file"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    return [line for line in open(filename).readlines() if line.strip()]


readme = open("README.rst").read()
history = open("CHANGELOG.rst").read().replace(".. :changelog:", "")

setup(
    name="bc-events",
    version=version,
    description="""A client for interacting with BriteCore's event hub.""",
    long_description=readme + "\n\n" + history,
    author="BriteCore",
    url="https://github.com/IntuitiveWebSolutions/bc-events",
    packages=["bc_events"],
    install_requires=get_requirements("requirements/base.txt"),
    zip_safe=False,
    keywords="britecore events hub pub sub",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
