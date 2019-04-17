
minX = None
minY = None
maxX = None
maxY = None

def plot_polylines(polylines, frame_width, frame_height, plot_fun, margin=10):
    global minX, minY, maxX, maxY

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

    ratio = min((frame_width-2*margin)/width, (frame_height-2*margin)/height)

    def tx(x):
        return (x-minX)*ratio+margin

    def ty(y):
        return (y-minY)*ratio+margin

    def plot(x1, y1, x2, y2):
        plot_fun(tx(x1), ty(y1), tx(x2), ty(y2))

    for line in polylines:
        if len(line.points) < 2:
            continue
        for p1, p2 in zip(line.points, line.points[1:]):
            plot(*p1, *p2)
        if line.connected:
            plot(*line.points[-1], *line.points[0])

from PIL import Image, ImageDraw

def draw_polylines_to_image_file(polylines, filename, width, height, bgcolor="#FFFFFF", stroke="#000000", strokewidth=2):
    img = Image.new('RGB', (width, height), color=bgcolor)

    draw = ImageDraw.Draw(img)

    def plot(*ps):
        draw.line(ps, fill=stroke, width=strokewidth)

    plot_polylines(polylines, width, height, plot_fun=plot)

    img.save(filename)
