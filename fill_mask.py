import math
from shapes import *
import sys
import numpy
import cairo
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import random

def GenerateRandomShape(min_radius, max_radius):
    r = random.random() * (max_radius - min_radius) + min_radius
    if random.random() < 0.1:
        return Square(0, 0, r, (random.random(), random.random(), random.random()))
    return Circle(0, 0, r, (random.random(), random.random(), random.random()))

def FindLocation(mask, shape, min_overlap_ratio=0.97):
    locations = []
    bb = shape.GetBoundingBox()
    checked = 0
    h = len(mask)
    w = len(mask[0])
    x0 = int(random.random() * 2)
    y0 = int(random.random() * 2)
    
    for y in xrange(x0, len(mask), 2):
        for x in xrange(y0, len(mask[y]), 2):
            checked += 1
            if mask[y][x]:
                min_x = int(max(0, math.floor(x + bb[0][0])))
                min_y = int(max(0, math.floor(y + bb[0][1])))
                max_x = int(min(w - 1, math.ceil(x + bb[1][0])))
                max_y = int(min(h - 1, math.ceil(y + bb[1][1])))
                overlap_area = 0.0
                shape_area = 0.0

                for y2 in xrange(min_y, max_y):
                    for x2 in xrange(min_x, max_x):
                        if shape.IsInside(x2 - x, y2 - y):
                            shape_area += 1.
                            if mask[y2][x2]:
                                overlap_area += 1.
                
                if overlap_area / shape_area >= min_overlap_ratio:
                    return (x, y)
                    locations.append((x, y))

    print 'Checked %d locations' % checked
    if locations == []:
        print 'There are no locations'
        return None
    index = int(math.floor(random.random() * len(locations)))
    return locations[index]

def ClearMask(mask, shape):
    shape.r += 1
    bb = shape.GetBoundingBox()
    min_x = int(math.floor(bb[0][0]))
    min_y = int(math.floor(bb[0][1]))
    max_x = int(math.ceil(bb[1][0]))
    max_y = int(math.ceil(bb[1][1]))

    cleared = 0
    for y in xrange(min_y, max_y):
        for x in xrange(min_x, max_x):
            if shape.IsInside(x, y):
                mask[y][x] = 0    
                cleared += 1
    print cleared
    
def main():
    """
    This is the main program.
    """
    image_name = sys.argv[1]
    image = mpimg.imread(image_name)

    image_width = len(image[0])
    image_height = len(image)
    mask = [[0 for x in xrange(0, image_width)]
            for y in xrange(0, image_height)]
    for y in xrange(0, len(mask)):
        for x in xrange(0, len(mask[y])):
            mask[y][x] = image[y][x][0] > 0
    #plt.imshow(mask)
    #plt.show(block=True)
    
    min_radius = 3
    max_radius = 20

    surface = cairo.SVGSurface(sys.argv[2], image_width, image_height)
    ctx = cairo.Context(surface)        

    shapes = []
    
    # Overall algorithm is this:
    # 1) Generate a random shape (within some given radius)
    # 2) Find random location inside of the mask to put the shape.
    #  - Exit if can't find some location.
    # 3) Clear those regions in the mask.
    # 4) Store circle in a list (and draw it)
    for i in xrange(0, 1000):
        shape = GenerateRandomShape(min_radius, max_radius)
        location = FindLocation(mask, shape)
        if not location:
            if max_radius > min_radius + 1:
                max_radius = (min_radius * 0.2 + max_radius * 0.8)
                print 'Shrinking max circle'
                continue
            break
        shape.x = location[0]
        shape.y = location[1]
        
        shape.Draw(ctx)

        ClearMask(mask, shape)
        shapes += [shape]

        if False:
            plt.hold(True)
            plt.imshow(mask)
            x = []
            y = []
            for shape in shapes:
                x.append(shape.x)
                y.append(shape.y)
                plt.plot(x, y, 'g*')
            plt.show()
            plt.hold(False)

    
if __name__ == '__main__':
    main()
