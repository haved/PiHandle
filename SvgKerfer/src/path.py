import numpy as np

class StraightLine:
    def __init__(self, relative_target):
        self.relative_target = relative_target

    def visit(self, visitor):
        return visitor.straight_line(self)

class QuadBez:
    def __init__(self, relative_target):
        self.relative_target = relative_target

    def visit(self, visitor):
        return visitor.quad_bez(self)


class CubeBez:
    def __init__(self, relative_target):
        self.relative_target = relative_target

    def visit(self, visitor):
        return visitor.cube_bez(self)


class Arc:
    def __init__(self, relative_target, rx, ry, big_sweep_flag, pos_dir_flag):
        self.relative_target = relative_target
        self.rx = rx
        self.ry = ry
        self.big_sweep_flag = big_sweep_flag
        self.pos_dir_flag = pos_dir_flag

    def visit(self, visitor):
        return visitor.arc(self)

class Path:
    def __init__(self, start_point, lines, connected, transform):
        self.start_point = start_point
        self.lines = lines
        self.connected = connected
        self.transform = transform
