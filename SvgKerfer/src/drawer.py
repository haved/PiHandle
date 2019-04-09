import matplotlib.pyplot as plt

def plot(p1, p2):
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]])

def draw_polylines(polylines):
    for line in polylines:
        for p1, p2 in zip(line.points, line.points[1:]):
            plot(p1, p2)
        if line.connected:
            plot(line.points[-1], line.points[0])

    plt.show()

