#!/usr/bin/env python

"""
Usage:
    python xyz2data.py <inputfile> <element1> ...

Example:
    python xyz2data.py quartz.xyz Si O
"""

import sys
from ase.io import read, write

d = read(sys.argv[1])
write(
    sys.argv[1].replace(".xyz", ".data"),
    d,
    format="lammps-data",
    specorder=sys.argv[2:],
)
