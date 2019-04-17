import numpy as np

class StraightLine:
    def __init__(self, target):
        self.target = target

    def visit(self, visitor):
        return visitor.straight_line(self)

class QuadBez:
    def __init__(self, p, target):
        self.p = p
        self.target = target

    def visit(self, visitor):
        return visitor.quad_bez(self)


class CubeBez:
    def __init__(self, p1, p2, target):
        self.p1 = p1
        self.p2 = p2
        self.target = target

    def visit(self, visitor):
        return visitor.cube_bez(self)


class Arc:
    def __init__(self, target, rx, ry, rot, big_sweep_flag, pos_dir_flag):
        self.rx = rx
        self.ry = ry
        self.rot = rot
        self.big_sweep_flag = big_sweep_flag
        self.pos_dir_flag = pos_dir_flag
        self.target = target

    def visit(self, visitor):
        return visitor.arc(self)

class Path:
    def __init__(self, start_point, lines, connected, transform):
        self.start_point = start_point
        self.lines = lines
        self.connected = connected
        self.transform = transform
