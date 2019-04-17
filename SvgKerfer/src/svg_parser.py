from lxml import etree
import numpy as np
from arg_parser import warning, error
from inspect import signature, Parameter
from maths import *
from path import *
from path_parser import parse_paths
import re

def get_pos_or_error(text, needle, pos, linenum):
    found = text.find(needle, pos)
    if found == -1:
        error(linenum, ": Expected ", needle, sep="")
    return found

def parse_transform(text, linenum):
    trans = np.identity(3)

    ops = [matrix, translate, rotate, scale, skewX, skewY]

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
        minArgs = sum(1 for x in params_taken if x.default==Parameter.empty)
        if len(vals) < minArgs or len(vals) > maxArgs:
            error(linenum, ": Wrong amount of parameters given to ", op_func.__name__, ". Got ", len(vals), " wanted ", minArgs, "-", maxArgs, sep="")

        trans = trans @ op_func(*vals)

        progress = end

    return trans

def get_floats(attr, *names):
    def pf(val):
        return float(val)
    return [pf(attr.get(x, "0")) for x in names]

def extract_paths(parent_transform, dom):
    result = []

    for child in dom:
        if child.tag is etree.Comment:
            continue
        tag = child.tag.split("}")[-1]
        attr = child.attrib
        transform = parent_transform.dot(parse_transform(attr.get("transform", ""), child.sourceline))
        if tag == "g":
            result += extract_paths(transform, child)
        elif tag == "circle":
            cx, cy, r = get_floats(attr, "cx", "cy", "r")
            result.append(Path([cx+r, cy], [Arc([cx-r, 0], r, r, 0, True, True), Arc([cx+r, 0], r, r, 0, True, True)], True, transform))
        elif tag == "ellipse":
            cx, cy, rx, ry = get_floats(attr, "cx", "cy", "rx", "ry")
            result.append(Path([cx+rx, cy], [Arc([cx-rx, 0], rx, ry, 0, True, True), Arc([cx+rx, 0], rx, ry, 0, True, True)], True, transform))
        elif tag == "rect":
            x, y, width, height, rx, ry = get_floats(attr, "x", "y", "width", "height", "rx", "ry")
            has_rounded_corners = "rx" in attr or "ry" in attr
            lines = []
            x2 = x + width
            y2 = y + height
            start_point = [x+rx, y]
            lines.append(StraightLine([x2-rx, y]))
            if has_rounded_corners:
                lines.append(Arc([x2, y+ry], rx, ry, 0, big_sweep_flag=False, pos_dir_flag=True))
            lines.append(StraightLine([x2, y2-ry]))
            if has_rounded_corners:
                lines.append(Arc([x2-rx, y2], rx, ry, 0, big_sweep_flag=False, pos_dir_flag=True))
            lines.append(StraightLine([x+rx, y2]))
            if has_rounded_corners:
                lines.append(Arc([x, y2-ry], rx, ry, 0, big_sweep_flag=False, pos_dir_flag=True))
            lines.append(StraightLine([x, y+ry]))
            if has_rounded_corners:
                lines.append(Arc([x+rx, y], rx, ry, 0, big_sweep_flag=False, pos_dir_flag=True))
            result.append(Path(start_point, lines, True, transform))
        elif tag == "polygon" or tag == "polyline":
            points = attr.get("points", "")
            coords = re.findall(r"-?[0-9]*\.?[0-9]*", points)
            coords = [float(x) for x in coords if x != "" and x != "-"]
            if len(coords) < 2:
                continue
            coords = list(zip(coords[::2], coords[1::2]))
            lines = [StraightLine(p1) for p1 in coords[1:]]
            result.append(Path(coords[0], lines, tag=="polygon", transform))
        elif tag == "path":
            d = attr.get("d", "")
            result += parse_paths(d, transform, child.sourceline)
        elif tag == "line":
            x1, y1, x2, y2 = get_floats(attr, "x1", "y1", "x2", "y2")
            p1 = [x1, y1]
            p2 = [x2, y2]
            result.append(Path(p1, [StraightLine(p2)], False, transform))
        elif tag == "title":
            print(child.sourceline, ": <title>",child.text,"</title>",sep="")
        else:
            warning("Ignoring tag:", tag)

    return result


def paths_of_svg_file(filename):
    with open(filename) as xml:
        root = etree.parse(xml).getroot()

    paths = extract_paths(np.identity(3), root)
    return paths

