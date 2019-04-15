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
        return [np.add(self.current_point, line.relative_target)]

    def arc(self, arc):
        A = self.current_point
        B = np.add(A, arc.relative_target)
        rx, ry = arc.rx, arc.ry
        rot = arc.rot
        big_sweep_flag = arc.big_sweep_flag
        pos_dir_flag = arc.pos_dir_flag

        if rx==0 or ry==0:
            return [B] #Just a straight line to the end

        right_of_AB = big_sweep_flag ^ (not pos_dir_flag)

        y_scale = rx/ry

        circle_space = maths.rotate(-rot) @ maths.scale(1, y_scale)
        inverse_circle = maths.scale(1, 1/y_scale) @ maths.rotate(rot)
        A_circle = transform(circle_space, A)
        B_circle = transform(circle_space, B)

        #Now we are working with a circle of radius rx
        radius = rx

        AB_circle = np.subtract(B_circle, A_circle)
        k = [-AB_circle[1], AB_circle[0]] #Rotate 90 degrees to the left
        if right_of_AB:
            k = np.dot(k, -1)
        k = normalize(k) #Orthogonal to AB_circle

        #Distance from AB line segment to center
        k_len = sqrt(radius**2 - (norm(AB_circle)/2)**2)
        center_circle = A_circle + AB_circle/2 + np.multiply(k, k_len)

        SA_circle = np.subtract(A_circle, center_circle)
        SB_circle = np.subtract(B_circle, center_circle)

        #Angle from center to points in degrees
        SA_angle = maths.angle([1, 0], SA_circle)
        SB_angle = maths.angle([1, 0], SB_circle)

        print("SA_angle: ", SA_angle)
        print("SB_angle: ", SB_angle)

        result = []
        for i in range(1, self.granularity):
            part = i / self.granularity
            diff = (SB_angle - SA_angle) % 360
            if not pos_dir_flag:
                diff -= 360
            angle = SA_angle + diff*part
            angle = radians(angle)
            result.append(np.add(center_circle, [cos(angle)*radius, sin(angle)*radius]))

        print("Done")

        return [transform(inverse_circle, x) for x in result]

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
