#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 17 March, 2020
"""
from setuptools import setup

setup(
    name = "MapCanvasGTK",
    version = "0.0.0",
    author = "Ben Knisley",
    author_email = "benknisley@gmail.com",
    description = ("A GTK Widget for adding interactive maps to your application."),
    url = "https://github.com/BenKnisley/MapCanvasGTK",
    license = "MIT",
    keywords = "GIS GTK map MapEngine GUI",
    #install_requires=['PyGObject', 'MapEngine'],
    #install_requires=['PyGObject'],
    packages=["MapCanvasGTK",],
    long_description="...",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
    ],
)


