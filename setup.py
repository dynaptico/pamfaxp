#!/usr/bin/env python

from distutils.core import setup

setup(
    name              = "dynaptico-pamfax",
    version           = "1.0.4",
    url               = "http://github.com/dynaptico/pamfaxp",
    author            = "Jonathan Sweemer",
    author_email      = "sweemer@gmail.com",
    maintainer        = "Dynaptico LLC (http://www.dynaptico.com)",
    maintainer_email  = "support@dynaptico.com",
    description       = "Python implementation of the PamFax API",
    long_description  = "This module implements a set of classes and methods for sending and receiving faxes via the PamFax API using the Python programming language",
    platforms         = ["Platform Independent"],
    license           = "MIT",
    packages          = ['pamfax', 'pamfax.processors'],
    classifiers       = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
)
