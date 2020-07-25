#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Created: 17 March, 2020
"""
from setuptools import setup

## Extract version from package __init__.py
from MapCanvasGTK import __version__ as version

## Get long description from readme file
with open('README.md') as f:
    long_desc_txt = f.read()



setup(
    name = "MapCanvasGTK",
    license = "MIT",
    version = version,
    author = "Ben Knisley",
    author_email = "benknisley@gmail.com",
    description = ("A PyGtk (PyGObject) widget for adding a map to your application"),
    url = "https://github.com/BenKnisley/MapCanvasGTK",
    keywords = "GIS GTK PyGObjects map PyMapKit GUI",
    install_requires=['PyMapKit', 'PyGObject'],
    packages=["MapCanvasGTK",],
    long_description=long_desc_txt,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
    ],
)


