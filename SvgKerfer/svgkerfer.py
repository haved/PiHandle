#!/usr/bin/env python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderSVG
from sys import argv

def print_help(exit_code=0):
    print("""Usage: svgKerfer <input files> [options]
    Example: svgKerfer oneFile.svg

    Input files supports the following wildcards: * and /**/
    Adds kerf to strokes in an svg.

    Options:
    -h --help                                    Prints this help message
    -c --color      <hex-code>=<kerf-amount>     Adds the given kerf to every stoke with the given color
    -d --default    <kerf-amount>                Sets the default kerf to give to stroke without color mapping
    -i --invert                                  Kerf adjusts inwards where it would do outwards and vice versa
    -o --output     <file names>                 Specifies the output file names. Default: %_kerfed.svg

    Will warn about non-handeled strokes unless a default kerf-amount is supplied. Disable with "-d 0"
    """)
    exit(exit_code)

def error(*a, **av):
    print("Error: ",end="")
    print(*a, **av)
    exit(1)

def parse_args(args):
    invert = False
    colors = {}
    default = None
    output = None
    inputs = []

    def expect_after(arg):
        args = args[1:]
        if len(args) == 0:
            error("Expected argument after '", arg, "'", sep="")

    while len(args) > 0:
        arg = args[0]
        if arg in ["-h", "--help"]:
            print_help()
        elif arg in ["-c", "--color"]:
            opt = expect_after(arg)
            split = opt.split('=')
            if len(split) != 2:
                error("Expected a single = sign after", arg)
            hexcol = int(split[0].strip(), 16)
            kerf = float(split[1].strip())

            if hexcol in colors:
                error("Defined color", hex(hexcol), "twice")

            colors[hexcol] = kerf
        elif arg in ["-d", "--default"]:
            opt = expect_after(arg)
            kerf = float(opt)

            if default != None:
                error("Defined default color twice")

            default = kerf
        elif arg in ["-i", "--invert"]:
            if invert:
                error("Error: Inverting more than once, what do you mean?")
            invert = True
        elif arg in ["-o", "--output"]:
            if output != None:
                error("Setting output multiple times")
            opt = expect_after(arg)
            output = opt
        elif arg.startswith("-"):
            print("Error: Unknown option", arg)
            print_help(1)
        else:
            inputs.push(arg)
        args = args[1:]

    return {"invert": invert, "colors": colors, "default": default, "output": output, "inputs":inputs}

from os import listdir
from os.path import join, isdir, isfile

def files_of_inputs(inputs):
    def files_of_input(dirlist, inp):
        found = False
        if "/" in inp:
            foldr,rest = inp.split("/", 1)
            if len(foldr) == 0:
                error("We don't support paths from root")
            for dir in dirlist:
                

    files = []
    for inp in inputs:
        files += files_of_input(listdir("."), inp)

options = parse_args(argv[1:])
input_files = files_of_inputs(options["inputs"]):

