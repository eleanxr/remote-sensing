#!/usr/bin/env python

from distutils.core import setup

base_requirements = [
    "numpy" # Probably need to fix a compatibility version here
]

gdal_kernel_requirements = [
#    "pygdal==1.10.1.0", # Version on Ubuntu 14.10
]

# TODO Parameterize this for conditional builds based
# on what's available.
requirements = base_requirements + gdal_kernel_requirements

setup(
    name="RemoteSensingTools",
    version="0.1",
    description="Remote Sensing Tools",
    url="http://wdicharry.github.io",
    author="Will Dicharry",
    author_email="wdicharry@gmail.com",
    install_requires=requirements,
    scripts=["landsattool.py"],
    test_suite="tests")


