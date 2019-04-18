from path import *
import numpy as np
from numpy.linalg import norm
import maths
from math import sin, cos, sqrt, radians

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

def normalize(vector):
    length = norm(vector)
    if length == 0:
        return vector
    return vector / length

class LinerVisitor:
    def __init__(self, granularity):
        self.granularity = granularity

    def set_current_point(self, point):
        self.current_point = point

    def straight_line(self, line):
        return [line.target]

    def arc(self, arc):
        p1 = self.current_point
        p2 = arc.target
        rx, ry = abs(arc.rx), abs(arc.ry)
        rot = arc.rot % 360
        big_sweep_flag = bool(arc.big_sweep_flag)
        pos_dir_flag = bool(arc.pos_dir_flag)

        if all(c1==c2 for c1,c2 in zip(p1, p2)):
            return []

        if rx==0 or ry==0:
            return [B] #Just a straight line to the end

        rot_trans = maths.rotate(rot)
        rot_trans_inv = maths.rotate(-rot)

        p1_prime = np.dot(np.subtract(p1, p2), .5)
        p1_prime = transform(rot_trans_inv, p1_prime)

        center_fac = 1 if big_sweep_flag != pos_dir_flag else -1
        center_dist = (rx*ry)**2 - (rx*p1_prime[1])**2 - (ry*p1_prime[0])**2
        center_dist /= (rx*p1_prime[1])**2 + (ry*p1_prime[0])**2
        if center_dist < 0:
            center_dist = 0
        center_dist = center_fac * sqrt(center_dist)

        center_prime = np.multiply([rx/ry, -ry/rx], p1_prime[::-1])
        center_prime = np.dot(center_prime, center_dist)
        center = transform(rot_trans, center_prime)
        center = np.add(center, np.dot(np.add(p1, p2), .5))

        def angle_to(p):
            return maths.angle([1,0], np.divide(np.subtract(p, center_prime), [rx, ry]))

        p1_prime_angle = angle_to(p1_prime) % 360
        p2_prime_angle = angle_to(np.dot(p1_prime, -1)) % 360

        angle_diff = (p2_prime_angle - p1_prime_angle) % 360
        if not pos_dir_flag:
            angle_diff -= 360

        def angle_to_point(angle):
            rad = radians(angle)
            return np.add(transform(rot_trans, [rx*cos(rad), ry*sin(rad)]), center)

        return [angle_to_point(p1_prime_angle + angle_diff * i / self.granularity) for i in range(1, self.granularity+1) ]

    def quad_bez(self, qb):
        b = self.current_point
        p = qb.p
        e = qb.target
        def func(t):
            sm = np.dot(b, (1-t)**2)
            sm = np.add(sm, np.dot(p, 2*(1-t)*t))
            sm = np.add(sm, np.dot(e, t**2))
            return sm

        return [func(i/self.granularity) for i in range(1, self.granularity+1)]

    def cube_bez(self, cb):
        b = self.current_point
        p1 = cb.p1
        p2 = cb.p2
        e = cb.target
        def func(t):
            sm = np.dot(b, (1-t)**3)
            sm = np.add(sm, np.dot(p1, 3*(1-t)**2*t))
            sm = np.add(sm, np.dot(p2, 3*(1-t)*t**2))
            sm = np.add(sm, np.dot(e, t**3))
            return sm

        return [func(i/self.granularity) for i in range(1, self.granularity+1)]

def polyline_of_path(path, granularity, epsilon):
    points = [path.start_point]

    visitor = LinerVisitor(granularity)
    for line in path.lines:
        visitor.set_current_point(points[-1])
        points += line.visit(visitor)

    points = [transform(path.transform, p) for p in points]

    fewer_points = points[0:1]
    for p2 in points:
        if dist(fewer_points[-1], p2) > epsilon:
            fewer_points.append(p2)
    if path.connected:
        while len(fewer_points) and (dist(fewer_points[0], fewer_points[-1]) <= epsilon):
            fewer_points.pop()

    return Polyline(fewer_points, path.connected)

def polylines_of_paths(paths, granularity, epsilon):
    return [polyline_of_path(path, granularity, epsilon) for path in paths]
