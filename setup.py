#!/usr/bin/env python

from distutils.core import setup

setup(name="mdtools",
      version="0.5",
      description="Tools for working with LAMMPS",
      author="Anders Johansson",
      author_email="anjohan@uio.no",
      url="github.com/anjohan/mdtools",
      scripts=["logplotter.py"]
)
