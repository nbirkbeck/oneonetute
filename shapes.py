import math

class Shape(object):
    def __init__(self, x, y, color=(0,0,0)):
        self.x = x
        self.y = y
        self.color = color
        
    def GetArea(self):
        raise NotImplementedError

class Circle(Shape):
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
        return 'position = (%d, %d), radius = %f' % (self.x, self.y, self.r)


class Square(Shape):
    def __init__(self, x, y, r, color=(0,0,0)):
        Shape.__init__(self, x, y, color)
        self.r = r

    def IsInside(self, x, y):
        r = self.r
        return (x >= self.x - r) and (x <= self.x + r) and (y >= self.y - r) and (y <= self.y + r)
            
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
        return 'position = (%d, %d), radius = %f' % (self.x, self.y, self.r)
