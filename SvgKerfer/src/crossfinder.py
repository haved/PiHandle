
class Cross:
    def __init__(self, pA, pB, pQ, pV):
        self.pA = pA
        self.pB = pB
        self.pQ = pQ
        self.pV = pV

    def to_polylines(self):
        return [Polyline([pA, pB], False), Polyline([pQ, pV], False)]

def crosses_among_polylines(polylines):
    pass

