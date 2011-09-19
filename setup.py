#!/usr/bin/env python

from distutils.core import setup

setup(
    name              = "pamfax",
    version           = "0.0.1",
    url               = "http://github.com/dynaptico/pamfaxp",
    maintainer        = "Dynaptico LLC",
    maintainer_email  = "support@dynaptico.com",
    description       = "Python implementation of the PamFax API",
    long_description  = "This module implements a set of classes and methods for sending and receiving faxes via the PamFax API using the Python programming language",
    platforms         = ["Platform Independent"],
    license           = "MIT",
    classifiers       = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    py_modules = ['pamfax'],
)
