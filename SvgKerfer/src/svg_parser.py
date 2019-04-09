from lxml import etree
import numpy as np
from arg_parser import warning, error
from inspect import signature, Parameter
from math import tan, cos, sin, radians
from maths import *
from path import *

def get_pos_or_error(text, needle, pos, linenum):
    found = text.find(needle, pos)
    if found == -1:
        error(linenum, ": Expected ", needle, sep="")
    return found

def parse_transform(text, linenum):
    trans = np.identity(3)

    ops = [matrix, translate, rotate, skewX, skewY]

    progress = 0
    while True:
        found = [(text.find(func.__name__, progress), func) for func in ops]
        found = list(filter(lambda x:x[0]>=0, found))
        if len(found) == 0:
            break
        found.sort(key = lambda x:x[0])
        op_pos = found[0][0]
        op_func = found[0][1]

        progress = get_pos_or_error(text, "(", op_pos, linenum)
        end = get_pos_or_error(text, ")", progress, linenum)
        vals = text[progress+1:end].split(",")
        vals = list(map(float, vals))

        params_taken = signature(op_func).parameters.values()
        maxArgs = len(params_taken)
        minArgs = sum(1 for x in params_taken if x.default!=Parameter.empty)
        if len(vals) < minArgs or len(vals) > maxArgs:
            error(linenum, ": Wrong amount of parameters given to ", op.__name__, ". Got ", len(vals), " wanted ", minArgs, "-", maxArgs, sep="")

        trans = trans @ op_func(*vals)

        progress = end

    return trans

def get_floats(attr, *names):
    def pf(val):
        return float(val)
    return [pf(attr.get(x, "0")) for x in names]

def extract_paths(transform, dom):
    result = []

    for child in dom:
        tag = child.tag.split("}")[-1]
        attr = child.attrib
        transform = transform.dot(parse_transform(attr.get("transform", ""), child.sourceline))
        if tag == "g":
            result += extract_paths(transform, child) #TODO: Check matrix mul order
        elif tag == "circle":
            cx, cy, r = get_floats(attr, "cx", "cy", "r")
            result.append(Path([cx+r, cy], Arc([0, 0], r, r, True, True), True, transform))
        elif tag == "ellipse":
            cx, cy, rx, ry = extract_paths(attr, "cx", "cy", "rx", "ry")
            result.append(Path([cx+r, cy], Arc([0, 0], rx, ry, True, True), True, transform))
        elif tag == "rect":
            x, y, width, height, rx, ry = get_floats(attr, "x", "y", "width", "height", "rx", "ry")
            has_rounded_corners = "rx" in attr or "ry" in attr
            lines = []
            start_point = [x+rx, y]
            lines.append(StraightLine([width-rx*2, 0]))
            if has_rounded_corners:
                lines.append(Arc([rx, ry], rx, ry, False, False))
            lines.append(StraightLine([0, height-ry*2]))
            if has_rounded_corners:
                lines.append(Arc([-rx, ry], rx, ry, False, False))
            lines.append(StraightLine([-width+rx*2, 0]))
            if has_rounded_corners:
                lines.append(Arc([-rx, -ry], rx, ry, False, False))
            lines.append(StraightLine([0, -height+ry*2]))
            if has_rounded_corners:
                lines.append(Arc([rx, -ry], rx, ry, False, False))
            result.append(Path(start_point, lines, True, transform))
        elif tag == "polygon":
            points = attr.get("points", "")
            trans = attr.get("transform", "")
            #TODO
        elif tag == "path":
            d = attr.get("d", "")
            trans = attr.get("transform", "")
            #TODO
        elif tag == "line":
            warning("Ignoring line") #TODO
        elif tag == "polyline":
            warning("Ignoring polyline") #TODO
        else:
            warning("Ignoring tag:", tag)

    return result


def paths_of_svg_file(filename):
    with open(filename) as xml:
        root = etree.parse(xml).getroot()

    paths = extract_paths(np.identity(3), root)
    return paths

