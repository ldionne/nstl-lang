#!/usr/bin/env python

from distutils.core import setup


setup(
    name = 'nstl',
    version = '0.1.0',
    url = 'https://github.com/ldionne/nstl-lang',
    author = 'Louis Dionne',
    author_email = 'louis.dionne92@gmail.com',
    description = 
        "nstl: A compiler for creating templates in C.",
    
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        # license ??
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Code Generators",
    ],
    
    packages = [
        'nstl',
    ],
    
    scripts = [
        'scripts/nstl.py',
    ],
)

