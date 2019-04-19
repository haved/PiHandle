from itertools import combinations
from liner import Poly

class Cross:
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2

    def to_polylines(self):
        return [Poly(self.line1, False), Poly(self.line2, False)]

def crosses_among_polys(polys):
    all_lines = []
    for poly in polys:
        for p1,p2 in zip(poly.points, poly.points[1:]):
            all_lines.append((p1, p2))
        if poly.connected:
            all_lines.append((poly.points[-1], poly.points[0]))

    for l1, l2 in combinations(all_lines, 2):
        pass

    return []

