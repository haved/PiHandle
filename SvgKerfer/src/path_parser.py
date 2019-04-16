import re
from path import *

def parse_paths(text, transform, linenum):
    result = []

    parts = re.findall(r"-?[0-9]*\.?[0-9]*|[A-Za-z]", text)

    current_path_start = [0,0]
    current_path_lines = []

    def finish_path(connect):
        nonlocal current_path_lines, current_coord
        if len(current_path_lines) != 0:
            result.append(Path(current_path_start, current_path_lines, connect, transform))
            current_path_lines = []
        if connect:
            current_coord = current_path_start

    current_coord = [0,0]

    parts = list(filter(lambda x:x!="", parts))

    def pop_part():
        nonlocal parts
        if len(parts) == 0:
            return None
        ret, *parts = parts
        return ret

    def get_float_opt():
        nonlocal parts
        if len(parts) == 0:
            return None
        try:
            front, *rest = parts
            front = float(front)
            parts = rest
            return front
        except:
            return None

    def get_global_coord_opt(relative):
        x, y = [get_float_opt(), get_float_opt()]
        if x == None or y == None:
            return None
        return [x + current_coord[0], y + current_coord[1]] if relative else [x, y]

    def get_relative_coord_opt(relative):
        x, y = [get_float_opt(), get_float_opt()]
        if x == None or y == None:
            return None
        return [x, y] if relative else [x - current_coord[0], y - current_coord[1]]

    while len(parts):
        p = pop_part()
        relative = p.islower()
        cmd = p.lower()

        if cmd == "m":
            current_coord = get_global_coord_opt(relative)
            finish_path(False) #We finish any path we might be currently doing
            current_path_start = current_coord
            cmd = "l"

        if cmd == "z":
            finish_path(True)
        elif cmd == "l":
            while True:
                relative_target = get_relative_coord_opt(relative)
                if not relative_target:
                    break

                current_path_lines.append(StraightLine(relative_target))
                current_coord = np.add(current_coord, relative_target)

        elif cmd == "h":
            while True:
                x = get_float_opt()
                if not x:
                    break
                if not relative:
                    current_coord[0] = 0
                current_coord[0] += x
                current_path_lines.append(StraightLine([x, 0]))
        elif cmd == "v":
            while True:
                y = get_float_opt()
                if not y:
                    break
                current_coord[1] += y
                current_path_lines.append(StraightLine([0, y]))
        elif cmd == "c":
            while True:
                p1 = get_relative_coord_opt(relative)
                p2 = get_relative_coord_opt(relative)
                relative_target = get_relative_coord_opt(relative)
                if not target:
                    break
                current_path_lines.append(QuadBez(p1, p2, relative_target))
                current_coord = np.add(current_coord, relative_target)
        elif cmd == "a":
            while True:
                rx, ry = get_float_opt(), get_float_opt()
                x_axis_rot = get_float_opt()
                large_arc_flag = get_float_opt() != 0.0
                pos_dir_flag = get_float_opt() != 0.0
                relative_target = get_relative_coord_opt(relative)
                if not relative_target:
                    break

                current_path_lines.append(Arc(relative_target, rx, ry, x_axis_rot, large_arc_flag, pos_dir_flag))
                current_coord = np.add(current_coord, relative_target)
        else:
            warning(linenum, ": Ignoring path data: ", p, sep="")

    finish_path(False)

    return result
