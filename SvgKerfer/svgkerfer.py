#!/usr/bin/env python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderSVG
from sys import argv
from arg_parser import *
from os.path import realpath

parser = ArgParser("svgkerfer [options] <input files>", "Adds kerf adjustments to stokes in an svg")
colors = DictOption(["-c", "--color"], "hex_code", "kerf", lambda x:int(x, 16), lambda x:float(x), "Adds kerf adjustment to all strokes of the given color")
default = NormalOption(["-d", "--default"], ["kerf"], "Adds a default kerf adjustment")
inverted = NormalOption(["-i", "--invert"], [], "Inverts whats insides and outsides")
output = NormalOption(["-o", "--output"], ["path"], "Format for output files. Default: '%_kerfed.svg'", '%_kerfed.svg')

parser.add(colors, default, inverted, output)
parser.take_args(argv[1:])

input_files = []
for code in parser.get_the_rest():
    files = file_code_to_file_paths(code)
    if len(files) == 0:
        error("No file found matching '", code, "'", sep="")
    input_files += [realpath(f) for f in files]

for fil in input_files:
    print(fil)
