
def get_bounding_box(polylines):
    minX = minY = maxX = maxY = None

    for polyline in polylines:
        for x,y in polyline.points:
            minX = min(minX, x) if minX else x
            maxX = max(maxX, x) if maxX else x
            minY = min(minY, y) if minY else y
            maxY = max(maxY, y) if maxY else y

    if minX == None:
        return None

    return [[minX, maxX], [minY, maxY]]

def plot_polylines(polylines, frame_width, frame_height, bounding_box, margin, plot_fun):

    width = bounding_box[0][1]-bounding_box[0][0]
    height = bounding_box[1][1]-bounding_box[1][0]

    ratio = min((frame_width-2*margin)/width, (frame_height-2*margin)/height)

    def tx(x):
        return (x-bounding_box[0][0])*ratio+margin

    def ty(y):
        return (y-bounding_box[1][0])*ratio+margin

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

def make_image(width, height, bgcolor="#FFFFFF"):
    return Image.new('RGB', (width, height), color=bgcolor)

def draw_polylines_to_image(img, polylines, bounding_box, margin=10, stroke="#000000", strokewidth=2):
    draw = ImageDraw.Draw(img)

    def plot(*ps):
        draw.line(ps, fill=stroke, width=strokewidth)

    plot_polylines(polylines, img.width, img.height, bounding_box, margin=margin, plot_fun=plot)

    return img
