#!/usr/bin/env python
from sys import argv
from arg_parser import *
from filehandler import get_input_output_list

outdef = "kerfed/%.svg"

parser = ArgParser("svgkerfer [options] <input files>", "Adds kerf adjustments to stokes in an svg")
colors = DictOption(["-c", "--color"], "hex_code", "kerf", lambda x:int(x, 16), lambda x:float(x), "Adds kerf adjustment to all strokes of the given color")
default = NormalOption(["-d", "--default"], ["kerf"], "Adds a default kerf adjustment")
inverted = NormalOption(["-i", "--invert"], [], "Inverts whats insides and outsides")
output = NormalOption(["-o", "--output"], ["path"], "Format for output files. Default: '%s'"%(outdef), outdef)
recursive = NormalOption(["-r", "--recursive"], [], "Allow converting entire directories")

parser.add(colors, default, inverted, output, recursive)
parser.take_args(argv[1:])

io = get_input_output_list(parser.get_the_rest(), recursive=recursive.is_set(), output=output.get_option())

for inp, out in io:
    print(inp, "->", out)
