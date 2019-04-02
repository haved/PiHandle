import xml.etree.ElementTree as ET
import tinycss2 as tcss2

def parse_css(text):
    rules = tcss2.parse_stylesheet(text, skip_comments=True, skip_whitespace=True)

#We only care about polygons, and ignore stroke width and don't keep transformations
def parse_svg_lines(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    css_classes = {}
    for tag in root.findall("style"):
        css_classes += parse_css(tag.text)

