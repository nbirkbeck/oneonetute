import math


class Shape(object):
    """A base class for a shape"""
    def __init__(self, x, y, color=(0,0,0)):
        self.x = x
        self.y = y
        self.color = color

    def IsInside(self, x, y):
        raise NotImplementedError
        
    def GetArea(self):
        raise NotImplementedError

    def GetBoundingBox(self):
        raise NotImplementedError

    def Draw(self, ctx):
        raise NotImplementedError

    def InsideRegion(self, w, h):
        bb = self.GetBoundingBox()
        min_x = int(max(0, math.floor(bb[0][0])))
        min_y = int(max(0, math.floor(bb[0][1])))
        max_x = int(min(w, math.ceil(bb[1][0])))
        max_y = int(min(h, math.ceil(bb[1][1])))
        for y in xrange(min_y, max_y):
            for x in xrange(min_x, max_x):
                if self.IsInside(x, y):
                    yield (x, y)


class Circle(Shape):
    """ A circle"""
    
    def __init__(self, x, y, r, color=(0,0,0)):
        Shape.__init__(self, x, y, color)
        self.r = r

    def IsInside(self, x, y):
        dx, dy = self.x - x,  self.y - y
        return dx*dx + dy*dy <= self.r * self.r
            
    def GetArea(self):
        return math.pi * self.r * self.r

    def GetBoundingBox(self):
        return ((self.x - self.r, self.y - self.r),
                (self.x + self.r, self.y + self.r))

    def Draw(self, ctx):
        color = self.color
        ctx.set_source_rgb(color[0], color[1], color[2])
        ctx.arc(self.x, self.y, self.r, 0., 2 * math.pi)
        ctx.fill()
        
    def __str__(self):
        return 'Circle @ (%d, %d), radius = %f' % (self.x, self.y, self.r)


class Square(Shape):
    """A square."""
    def __init__(self, x, y, r, color=(0,0,0)):
        Shape.__init__(self, x, y, color)
        self.r = r
        
    def IsInside(self, x, y):
        r = self.r
        return ((x >= self.x - r) and (x <= self.x + r) and
                (y >= self.y - r) and (y <= self.y + r))
            
    def GetArea(self):
        return 4 * self.r * self.r

    def GetBoundingBox(self):
        return ((self.x - self.r, self.y - self.r),
                (self.x + self.r, self.y + self.r))

    def Draw(self, ctx):
        color = self.color
        r = self.r
        ctx.set_source_rgb(color[0], color[1], color[2])
        ctx.move_to(self.x - r, self.y - r)
        ctx.line_to(self.x + r, self.y - r)
        ctx.line_to(self.x + r, self.y + r)
        ctx.line_to(self.x - r, self.y + r)
        ctx.line_to(self.x - r, self.y - r)
        ctx.fill()
        
    def __str__(self):
        return 'Square @ (%d, %d), radius = %f' % (self.x, self.y, self.r)
