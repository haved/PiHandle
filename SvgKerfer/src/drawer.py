import Tkinter

def draw_polylines(polylines):
    window = Tkinter.Tk()
    canva = Tkinter.Canvas(window)

    for line in polylines:
        for p1, p2 in zip(line.lines, line.lines[:1]):
            canva.create_line(*p1, *p2)
        if line.connected:
            canva.create_line(*line.lines[-1], *line.lines[0])

    canva.pack()

