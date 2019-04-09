import numpy as np
from math import sin, cos, tan, radians

def matrix(a, b, c, d, e, f):
    return np.matrix([[a, b, c], [d, e, f], [0, 0, 1]])
def translate(x, y=0):
    return np.matrix([[1, 0, x], [0, 1, y], [0, 0, 1]])
def scale(sx, sy=None):
    if sy == None:
        sy = sx
    return np.matrix([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
def rotate(a, cx=0, cy=0):
    if cx != 0 or cy != 0:
        return translate(cx, cy) @ rotate(a) @ translate(-cx, -cy)
    a = radians(a)
    return np.matrix([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])
def skewX(a):
    a = radians(a)
    return np.matrix([[1, tan(a), 0], [0, 1, 0], [0, 0, 1]])
def skewY(a):
    a = radians(a)
    return np.matrix([[1, 0, 0], [tan(a), 1, 0], [0, 0, 1]])
