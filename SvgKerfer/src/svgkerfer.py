#!/usr/bin/env python
from sys import argv
from arg_parser import *
from logger import *
from filehandler import get_input_output_list
from svg_parser import paths_of_svg_file
from liner import polys_of_paths
from drawer import *
from crossfinder import crosses_among_polys

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

    polys = polys_of_paths(paths, gran, epsi)
    polygons = [p for p in polys if p.connected]
    polylines = [p for p in polys if not p.connected]

    if len(polylines) != 0:
        warning("Polylines found, will not be kerf adjusted: Display?", end="")
        if input_yn(default=False):
            image = make_image(800, 480)
            bounding_box = get_bounding_box(polys)
            draw_polylines_to_image(image, polygons, bounding_box, strokewidth=1, stroke="black")
            draw_polylines_to_image(image, polylines, bounding_box, strokewidth=2, stroke="red")
            image.show()

    crossings = crosses_among_polys(polygons)

    if len(crossings) != 0:
        error("Crossing lines were found among the polygons. Do you want to see?", end="", fatal=False)
        if input_yn(default=True):
            image = make_image(800, 480)
            bounding_box = get_bounding_box(polys)
            draw_polylines_to_image(image, polys, bounding_box, strokewidth=1, stroke="black")
            cross_polylines = [line for c in crossings for line in c.to_polylines()]
            draw_polylines_to_image(image, cross_polylines, bounding_box, strokewidth=2, stroke="red")
            image.show()
        error("Aborting due to previous error")

    #TODO: Separate polygons into inside and outside egdes

    if display.is_set():
        #TODO: Kerf adjusted polys
        info("Showing result...")
        draw_polylines_to_image(make_image(800, 480), polys, get_bounding_box(polys), strokewidth=1).show()

    info("Done")

