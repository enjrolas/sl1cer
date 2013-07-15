#!/usr/bin/python

import sys
from Slicer import *

slicer=Slicer()

slicer.load(sys.argv[1])

slicer.scale(45, 45, 60.0)
slicer.slice(2, rows=6, cols=4, margin=5, padding=0) #0.3mm slices, in a 4x4 grid
