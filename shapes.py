import math

class Shape(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def GetArea(self):
        raise NotImplementedError

    def GetBoundingBox(self):
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, x, y, r):
        Shape.__init__(self, x, y)
        self.r = r

    def GetArea(self):
        return math.pi * self.r * self.r

    def __str__(self):
        return 'position = (%d, %d), radius = %f' % (self.x, self.y, self.r)

