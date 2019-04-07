from lxml import etree
import numpy as np
from arg_parser import warning, error
from inspect import signature, Parameter
from math import tan, cos, sin, radians

# We only care about paths, and ignore stroke width and don't keep transformations
# The path is a list of tuples of the form (char, *data)

def get_pos_or_error(text, needle, pos, linenum):
    found = text.find(needle, pos)
    if found == -1:
        error(linenum, ": Expected ", needle, sep="")
    return found

def parse_transform(text, linenum):
    trans = np.identity(3)

    def matrix(a, b, c, d, e, f):
        return np.matrix([[a, b, c], [d, e, f], [0, 0, 1]])
    def translate(x, y=0):
        return np.matrix([[1, 0, x], [0, 1, y], [0, 0, 1]])
    def scale(sx, sy=None):
        if sy == None:
            sy = sx
        return np.matrix([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
    def rotate(a, cx=0, cy=0):
        if cx != 0 or xy != 0:
            return translate(cx, cy) @ rotate(a) @ translate(-cx, -cy)
        a = radians(a)
        return np.matrix([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])
    def skewX(a):
        a = radians(a)
        return np.matrix([[1, tan(a), 0], [0, 1, 0], [0, 0, 1]])
    def skewY(a):
        a = radians(a)
        return np.matrix([[1, 0, 0], [tan(a), 1, 0], [0, 0, 1]])

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

def extract_paths(transform, dom):
    result = []

    for child in dom:
        tag = child.tag.split("}")[-1]
        attr = child.attrib
        if tag == "g":
            transform_str = attr.get("transform", "")
            trans = parse_transform(transform_str, child.sourceline)
            result += extract_paths(transform.dot(trans), child) #TODO: Check matrix mul order
        elif tag == "circle":
            cx = attr.get("cx", 0)
            cy = attr.get("cy", 0)
            r = attr.get("r", 0)
            trans = attr.get("transform", "")
            #TODO
        elif tag == "ellipse":
            cx = attr.get("cx", 0)
            cy = attr.get("cy", 0)
            rx = attr.get("rx", 0)
            ry = attr.get("ry", 0)
            trans = attr.get("transform", "")
            #TODO
        elif tag == "rect":
            x = attr.get("x", 0)
            y = attr.get("y", 0)
            width = attr.get("width", 0)
            height = attr.get("height", 0)
            rx = attr.get("rx", 0)
            ry = attr.get("ry", 0)
            trans = attr.get("transform", "")
            #TODO
        elif tag == "polygon":
            points = attr.get("points", "")
            trans = attr.get("transform", "")
            #TODO
        elif tag == "path":
            d = attr.get("d", "")
            trans = attr.get("transform", "")
            #TODO
        elif tag == "line":
            warning("Ignoring line")
        elif tag == "polyline":
            warning("Ignoring polyline")
        else:
            warning("Ignoring tag:", tag)

    return result


def paths_of_svg(filename):
    with open(filename) as xml:
        root = etree.fromstring(xml.read())

    polygons = extract_paths(np.identity(3), root)
    return polygons

