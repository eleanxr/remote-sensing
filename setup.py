#!/usr/bin/env python

from distutils.core import setup

setup(
    name="RemoteSensingTools",
    version="0.1",
    description="Remote Sensing Tools",
    author="Will Dicharry",
    author_email="wdicharry@gmail.com",
    install_requires = [
        "numpy",
        "pygdal==1.10.1.0" # Use plain 'gdal' for older gdals)
        ]
    )


