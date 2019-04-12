from path import *
import numpy as np
from numpy.linalg import norm

class Polyline:
    def __init__(self, points, connected):
        self.points = points
        self.connected = connected

def dist(p1, p2):
    return norm(np.subtract(p1,p2))

def transform(trans, p):
    p = np.append(p, 1)
    p = np.dot(trans, p)
    p = np.asarray(p).reshape(-1)
    return p[:2]

class LinerVisitor:
    def __init__(self, granularity):
        self.granularity = granularity

    def set_current_point(self, point):
        self.current_point = point

    def straight_line(self, line):
        return [np.add(self.current_point, line.relative_target)]

    def arc(self, arc):
        return []

def polyline_of_path(path, granularity, epsilon):
    points = [path.start_point]

    visitor = LinerVisitor(granularity)
    for line in path.lines:
        visitor.set_current_point(points[-1])
        points += line.visit(visitor)

    points = [transform(path.transform, p) for p in points]

    if path.connected:
        points = [p for p,p2 in zip(points, points[1:]+points[:1]) if dist(p, p2)>epsilon]
    else:
        last_point = points[-1]
        points = [p for p,p2 in zip(points, points[1:]) if dist(p, p2)>epsilon]
        points.append(last_point)

    return Polyline(points, path.connected)

def polylines_of_paths(paths, granularity, epsilon):
    return [polyline_of_path(path, granularity, epsilon) for path in paths]
