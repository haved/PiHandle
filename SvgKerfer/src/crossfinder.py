from itertools import combinations
from liner import Poly
import numpy as np

class Cross:
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2

    def to_polylines(self):
        return [Poly(self.line1, False), Poly(self.line2, False)]

epsilon = 1e-10
def cross(line1, line2):
    p, r = line1
    r = np.subtract(r, p) # r is the line vector
    r_squared = np.dot(r,r)

    q, s = line2
    s = np.subtract(s, q) # s is the line vector
    s_squared = np.dot(s,s)

    if r_squared < epsilon or s_squared < epsilon:
        return False

    # Say there is t and u such that: p + t*r = q + u*s
    rs = np.cross(r, s)

    q_min_p = np.subtract(q, p)
    q_min_p_cross_r = np.cross(q_min_p, r)

    if rs == 0:
        if q_min_p_cross_r == 0: #Colinear
            q_as_t = np.dot(np.subtract(q, p), r) / r_squared
            qs_as_t = q_as_t + np.dot(s, r) / r_squared
            return q_as_t > 0 and q_as_t < 1 or qs_as_t > 0 and qs_as_t < 1
        else: #Parallell, but different lines
            return False

    t = np.cross(q_min_p, s) / rs
    u = q_min_p_cross_r / rs

    if 0 < t < 1 and 0 < u < 1: #We don't care about sharing end points
        return True

def crosses_among_polys(polys):
    # Now we could do this O((n+k)log(n)), but I don't want to implement a priority queue or set in python
    # O(n²) it is :)

    all_lines = []

    crosses = []
    for poly in polys:
        for p1,p2 in zip(poly.points, poly.points[1:]):
            all_lines.append((p1, p2))
        if poly.connected and len(poly.points) > 2:
            all_lines.append((poly.points[-1], poly.points[0]))

    if len(all_lines) > 1000:
        print("Given", len(all_lines), "line segments. Checking for crosses")

    for l1, l2 in combinations(all_lines, 2):
        if cross(l1, l2):
            crosses.append(Cross(l1, l2))

    return crosses

