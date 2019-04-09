from path import *
import numpy as np
from numpy.linalg import norm

class Polyline:
    def __init__(self, points, connected):
        self.points = points
        self.connected = connected

def dist(p1, p2):
    return norm(p1-p2)

def transform(trans, p):
    #print("Transform:", trans)
    #print("Start:", p)
    p = np.append(p, 1)
    #p = np.transpose(p)
    #print("Her:", p)
    p = np.dot(trans, p)
    #print("Nå:", p)
    #p = np.transpose(p)
    #print("Etter:", p)
    p = p[:2]
    #print("Ferdig:", p)
    return p

def polyline_of_path(path, granularity):
    points = []

    current_point = path.start_point
    points.append(current_point)

    for line in path.lines:
        new_point = np.add(current_point, line.relative_target)
        #TODO: Divide up arcs and beziers, use the eigenvalue of the transform to scale the granularity
        points.append(new_point)
        current_point = new_point

    points = [transform(path.transform, p) for p in points]

    if path.connected:
        points = [p for p,p2 in zip(points, points[1:]+points[:1]) if dist(p, p2)>granularity/10]
    else:
        points = [p for p,p2 in zip(points, points[1:]) if dist(p, p2)>granularity/10]+points[-1]

    return points

def polylines_of_paths(paths, granularity):
    return [polyline_of_path(path, granularity) for path in paths]
