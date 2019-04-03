import xml.etree.ElementTree as ET
import numpy as np
from arg_parser import warning

# We only care about polygons, and ignore stroke width and don't keep transformations

def parse_transform(text):
    trans = np.identity(3)

    def matrix(args):
        pass
    def translate(args):
        pass
    def rotate(args):
        pass
    def skewX(args):
        pass
    def skewY(args):
        pass

    ops = [matrix, translate, rotate, skewX, skewY]

    progress = 0
    while True:
        found = [(text.find(func.__name__, progress), func) for func in ops]
        found = filter(lambda x:x[0]>=0, found)
        if len(found) == 0:
            break
        found.sort(key = lambda x:x[0])

def pn(text):
    return float(text)

def extract_polygons(transform, dom):

    result = []

    for child in dom:
        tag = child.tag
        attr = child.attrib
        if tag == "g":
            transform_str = attr.get("transform", "")
            trans = parse_transform(transform_str)
            result += extract_polygons(transform.dot(trans)) #TODO: Check order
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


def polygons_of_svg(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    polygons = extract_polygons(np.identity(3), root)
    return polygons

