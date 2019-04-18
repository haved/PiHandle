#!/usr/bin/env python
from sys import argv
from arg_parser import *
from logger import *
from filehandler import get_input_output_list
from svg_parser import paths_of_svg_file
from liner import polylines_of_paths
from drawer import draw_polylines_to_image

outdef = "kerfed/%.svg"

parser = ArgParser("svgkerfer [options] <input files>", "Adds kerf adjustments to stokes in an svg")
#colors = DictOption(["-c", "--color"], "hex_code", "kerf", lambda x:int(x, 16), lambda x:float(x), "Adds kerf adjustment to all strokes of the given color")
default = NormalOption(["-k", "--kerf"], ["kerf"], "Sets a kerf adjustment")
inverted = NormalOption(["-i", "--invert"], [], "Inverts whats insides and outsides")
granularity = NormalOption(["-g"], ["granularity"], "Line segments per curve / ellipse. Default:30", 30)
epsilon = NormalOption(["-e"], ["epsilon"], "Minimum distance between two neighbouring points. Default: .0", 0)
display = NormalOption(["-v", "--visual"], [], "Draws the output to a window")
output = NormalOption(["-o", "--output"], ["path"], "Format for output files. Default: '%s'"%(outdef), outdef)
recursive = NormalOption(["-r", "--recursive"], [], "Allow converting entire directories")

parser.add(default, inverted, granularity, epsilon, display, output, recursive)
parser.take_args(argv[1:])

io = get_input_output_list(parser.get_the_rest(), recursive=recursive.is_set(), output=output.get_option())

gran = int(granularity.get_option())
epsi = float(epsilon.get_option())

for inp, out in io:
    print(inp, "->", out)
    paths = paths_of_svg_file(inp)

    polylines = polylines_of_paths(paths, gran, epsi)

    #if display.is_set():
    #    draw_polylines_to_image(polylines, 800, 480, strokewidth=1).show()

    for i in range(200):
        epsilon = (i/14)**2.7
        polylines = polylines_of_paths(paths, gran, epsilon)
        filename = "anim/image{}.jpg".format(i)
        print("Saving:", filename)
        draw_polylines_to_image(polylines, 1920*2, 1080*2, strokewidth=4).save(filename)
