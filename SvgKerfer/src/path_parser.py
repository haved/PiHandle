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
    prev_helper_vector = [0,0]

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

    def get_coord_opt(relative):
        x, y = [get_float_opt(), get_float_opt()]
        if x == None or y == None:
            return None
        return [x + current_coord[0], y + current_coord[1]] if relative else [x, y]

    while len(parts):
        p = pop_part()
        relative = p.islower()
        cmd = p.lower()
        helper_vector_set = False

        if cmd == "m":
            current_coord = get_coord_opt(relative)
            finish_path(False) #We finish any path we might be currently doing
            current_path_start = current_coord
            cmd = "l"

        if cmd == "z":
            finish_path(True)
        elif cmd == "l":
            while True:
                target = get_coord_opt(relative)
                if target==None:
                    break

                current_path_lines.append(StraightLine(target))
                current_coord = target

        elif cmd == "h":
            while True:
                x = get_float_opt()
                if x==None:
                    break
                current_coord = np.add(current_coord, [x, 0]) if relative else [x, 0]
                current_path_lines.append(StraightLine(current_coord))
        elif cmd == "v":
            while True:
                y = get_float_opt()
                if y==None:
                    break
                current_coord = np.add(current_coord, [0, y]) if relative else [0, y]
                current_path_lines.append(StraightLine(current_coord))
        elif cmd == "c" or cmd == "s":
            while True:
                p1 = get_coord_opt(relative) if cmd == "c" else np.subtract(current_coord, prev_helper_vector)
                p2 = get_coord_opt(relative)
                target = get_coord_opt(relative)
                if target==None:
                    break
                current_path_lines.append(CubeBez(p1, p2, target))
                current_coord = target
                helper_vector_set = True
                prev_helper_vector = np.subtract(p2, target)
        elif cmd == "q" or cmd == "t":
            while True:
                p = get_coord_opt(relative) if cmd == "q" else np.subtract(current_coord, prev_helper_vector)
                target = get_coord_opt(relative)
                if target==None:
                    break
                current_path_lines.append(QuadBez(p, target))
                current_coord = target
                helper_vector_set = True
                prev_helper_vector = np.subtract(p, target)
        elif cmd == "a":
            while True:
                rx, ry = get_float_opt(), get_float_opt()
                x_axis_rot = get_float_opt()
                large_arc_flag = get_float_opt() != 0.0
                pos_dir_flag = get_float_opt() != 0.0
                target = get_coord_opt(relative)
                if target==None:
                    break

                current_path_lines.append(Arc(target, rx, ry, x_axis_rot, large_arc_flag, pos_dir_flag))
                current_coord = target
        else:
            warning(linenum, ": Ignoring path data: ", p, sep="")
        if not helper_vector_set:
            prev_helper_vector = [0,0]

    finish_path(False)

    return result
