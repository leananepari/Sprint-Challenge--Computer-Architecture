#!/usr/bin/env python3

"""Main."""

import sys
import os
from cpu import *
from ast import literal_eval

path = "sctest.ls8"

cpu = CPU()
cpu.load(path)
cpu.run()