import tkinter as tk

WIDTH=800
HEIGHT=480

def draw_polylines(polylines):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)

    minX = None
    minY = None
    maxX = None
    maxY = None

    for line in polylines:
        for x,y in line.points:
            minX = min(minX, x) if minX else x
            minY = min(minY, y) if minY else y
            maxX = max(maxX, x) if maxX else x
            maxY = max(maxY, y) if maxY else y

    if minX == None:
        warning("Svg empty, nothing to show")
        return

    width = maxX-minX
    height = maxY-minY

    ratio = min((WIDTH-20)/width, (HEIGHT-20)/height)

    def tx(x):
        return (x-minX)*ratio+10

    def ty(y):
        return (y-minY)*ratio+10

    def plot(x1, y1, x2, y2):
        canvas.create_line(tx(x1), ty(y1), tx(x2), ty(y2))

    for line in polylines:
        if len(line.points) < 2:
            continue
        for p1, p2 in zip(line.points, line.points[1:]):
            plot(*p1, *p2)
        if line.connected:
            plot(*line.points[-1], *line.points[0])

    canvas.pack()

    root.mainloop()

