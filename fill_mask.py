import math
from shapes import *
import sys
import numpy
import cairo
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from random import random as rand

def GenerateRandomShape(min_radius, max_radius):
    """
    Generates a random shape with uniformly distributed radius in the range of
    min radius and max radius.
    
    Args:
      min_radius: the minimum radius of hte shape.
      max_radius: the maximum radius of the shape.
    
    Returns:
      A random shape.
    """
    r = rand() * (max_radius - min_radius) + min_radius
    if rand() < 1.0:
        return Square(0, 0, r, (rand(), rand(), rand()))
    return Circle(0, 0, r, (rand(), rand(), rand()))


def FindLocation(mask, shape, min_overlap_ratio=0.97):
    """
    Finds a location to place the shape using the mask as the valid regions.
    
    Args:
      mask: the input mask (2d binary image)
      shape: the shape that we wish to place.
      min_overlap_ratio: the minimum overlap ratio of the shape with the mask.
    
    Returns:
      A pair of integers (the location), or None if there is no more space.
    """
    locations = []
    bb = shape.GetBoundingBox()
    checked = 0
    h = len(mask)
    w = len(mask[0])
    x0 = int(rand() * 2)
    y0 = int(rand() * 2)
    
    for y in xrange(x0, h, 2):
        for x in xrange(y0, w, 2):
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
    index = int(math.floor(rand() * len(locations)))
    return locations[index]

def ClearMask(mask, shape):
    shape.r += 0.5
    bb = shape.GetBoundingBox()
    h = len(mask)
    w = len(mask[0])
    min_x = max(0, int(math.floor(bb[0][0])))
    min_y = max(0, int(math.floor(bb[0][1])))
    max_x = min(w, int(math.ceil(bb[1][0])))
    max_y = min(h, int(math.ceil(bb[1][1])))
    for y in xrange(min_y, max_y):
        for x in xrange(min_x, max_x):
            if shape.IsInside(x, y):
                mask[y][x] = 0    

def SetColorFromImage(image, shape):
    shape.r += 1
    bb = shape.GetBoundingBox()
    h = len(image)
    w = len(image[0])
    min_x = max(0, int(math.floor(bb[0][0])))
    min_y = max(0, int(math.floor(bb[0][1])))
    max_x = min(w, int(math.ceil(bb[1][0])))
    max_y = min(h, int(math.ceil(bb[1][1])))

    cleared = 0
    colors = []
    for y in xrange(min_y, max_y):
        for x in xrange(min_x, max_x):
            if shape.IsInside(x, y):
                colors.append((
                    float(image[y][x][0]),
                    float(image[y][x][1]),
                    float(image[y][x][2]))
                )
    index = int(math.floor(rand() * len(colors)))
    shape.color = colors[index]
    print shape.color
    
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
            mask[y][x] = image[y][x][0] > 0 or image[y][x][1] > 0 or image[y][x][2] > 0
    #plt.imshow(mask)
    #plt.show(block=True)
    
    min_radius = 1
    max_radius = 2.5

    surface = cairo.SVGSurface(sys.argv[2], image_width, image_height)
    ctx = cairo.Context(surface)        

    shapes = []
    
    # Overall algorithm is this:
    # 1) Generate a random shape (within some given radius)
    # 2) Find random location inside of the mask to put the shape.
    #  - Exit if can't find some location.
    # 3) Clear those regions in the mask.
    # 4) Store circle in a list (and draw it)
    for i in xrange(0, 100000):
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
        SetColorFromImage(image, shape)
        
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
