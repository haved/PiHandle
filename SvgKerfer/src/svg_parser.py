from lxml import etree
import numpy as np
from arg_parser import warning, error
from inspect import signature, Parameter
from maths import *
from path import *
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

def parse_paths(text, transform, linenum):
    result = []

    parts = re.findall(r"[0-9]*\.?[0-9]*|[A-Za-z]", text)

    current_path_start = [0,0]
    current_path_lines = []

    def finish_path(connect):
        nonlocal current_path_lines, current_coord
        if len(current_path_lines) != 0:
            result.append(Path(current_path_start, current_path_lines, connect, transform))
            current_path_lines = []
        if connect:
            current_coord = current_path_start

    current_coord = [0,0]

    float_stack = []
    def pop_coord(relative=False):
        nonlocal float_stack, current_coord
        x, y, *float_stack = float_stack
        return [x + current_coord[0], y + current_coord[1]] if relative else [x, y]

    for p in parts[::-1]:
        relative = p.islower()
        cmd = p.lower()

        if cmd == "m":
            current_coord = pop_coord(relative)
            finish_path(False) #We finish any path we might be currently doing
            current_path_start = current_coord
            cmd = "l"

        if cmd == "z":
            finish_path(True)
        elif cmd == "l":
            while len(float_stack) >= 2:
                coord = pop_coord(relative)
                diff = np.subtract(coord, current_coord)
                current_path_lines.append(StraightLine(diff))
                current_coord = coord
        elif cmd == "h":
            while len(float_stack) >= 1:
                x, *float_stack = float_stack
                line_len = x if relative else x-current_coord[0]
                current_path_lines.append(StraightLine([line_len, 0]))
                current_coord[0] += line_len
        elif cmd == "v":
            while len(float_stack) >= 1:
                y, *float_stack = float_stack
                line_len = y if relative else x-current_coord[1]
                current_path_lines.append(StraightLine([0, line_len]))
                current_coord[1] += line_len
        elif cmd == "c" or cmd=="s" or cmd=="q" or cmd=="t" or cmd=="a":
            pass
        elif p != "":
            float_stack.insert(0, float(p))

    finish_path(False)

    return result

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
        elif tag == "polygon" or tag == "polyline":
            points = attr.get("points", "")
            coords = re.findall(r"[0-9]*\.?[0-9]*", points)
            coords = [float(x) for x in coords if x != ""]
            if len(coords) < 2:
                continue
            coords = zip(coords[::2], coords[1::2])
            lines = [StraightLine(np.sub(p2,p1)) for p1,p2 in zip(coords, coords[1:])]
            result.append(Path(coords[0], lines, transform, tag=="polygon"))
        elif tag == "path":
            d = attr.get("d", "")
            result += parse_paths(d, transform, child.sourceline)
        elif tag == "line":
            x1, y1, x2, y2 = get_floats(attr, "x1", "y1", "x2", "y2")
            p1 = [x1, y1]
            p2 = [x2, y2]
            result.append(Path(p1, [StraightLine(np.subtract(p2,p1))], False, transform))
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

