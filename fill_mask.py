"""
Application to fill an image mask with some random shapes and
assign the shapes a color based on the input image or some 
specified set of colors.
"""
import math
from shapes import *
from optparse import OptionParser
import sys
import numpy
import cairo
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from random import random as rand


def GenerateRandomShape(min_radius, max_radius, class_type=Circle):
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
    return class_type(0, 0, r, (rand(), rand(), rand()))


def FindLocation(mask, shape, min_overlap_ratio=0.97, use_first_location=True):
    """
    Finds a location to place the shape using the mask as the valid regions.
    
    Args:
      mask: the input mask (2d binary image)
      shape: the shape that we wish to place.
      min_overlap_ratio: the minimum overlap ratio of the shape with the mask.
      use_first_location: whether to use the first viable location or not.

    Returns:
      A pair of integers (the location), or None if there is no more space.
    """
    locations = []
    checked = 0
    w, h = len(mask[0]), len(mask)
    
    for y in xrange(int(rand() * 2), h, 2):
        for x in xrange(int(rand() * 2), w, 2):
            checked += 1
            if mask[y][x]:
                overlap_area, shape_area = 0.0, 0.0
                shape.x, shape.y = x, y
                for point in shape.InsideRegion(w, h):
                    shape_area += 1
                    if mask[point[1]][point[0]]:
                        overlap_area += 1
                
                if overlap_area / shape_area >= min_overlap_ratio:
                    if use_first_location:
                        return (x, y)
                    locations.append((x, y))

    print 'Checked %d locations' % checked
    if locations == []:
        print 'There are no locations'
        return None

    index = int(math.floor(rand() * len(locations)))
    return locations[index]


def ClearMask(mask, shape, padding=1.):
    """
    Clears the region in the mask that is occupied by the shape.
    
    Args:
      mask: the occupancy mask.
      shape: the shape which we have placed.
      padding: the amount to grow the shapes radius.
    """
    shape.r += padding
    for point in shape.InsideRegion(len(mask[0]), len(mask)):
        mask[point[1]][point[0]] = 0    


def SetColorFromImage(image, shape):
    """
    Assigns the color of the shape from a random color from the image
    area that it overlaps.

    Args:
      image: the input image to use when sourcing the color.
      shape: the shape.
    """
    colors = []
    for point in shape.InsideRegion(len(image[0]), len(image)):
        colors.append(image[point[1]][point[0]][:])
    if colors == []: return
    shape.color = colors[int(math.floor(rand() * len(colors)))]


def WriteShapes(filename, shapes, width, height):
    """
    Writes a list of shapes to the given filename.
    """
    surface = cairo.SVGSurface(filename, width, height)
    ctx = cairo.Context(surface)        
    for shape in shapes:
        shape.Draw(ctx)


def FillMaskWithShapes(mask, generate_shape, set_color, min_radius=1., max_radius=2.5):
    """
    Fills the mask with a randomly generated shape.

    Overall algorithm:
    1) Generate a random shape (within some given radius)
    2) Find random location inside of the mask to put the shape.
     - Exit if can't find some location.
    3) Clear those regions in the mask.
    4) Store circle in a list (and draw it)
    """
    shapes = []
    for i in xrange(0, 100000):
        shape = generate_shape(min_radius, max_radius)
        location = FindLocation(mask, shape)
        if not location:
            if max_radius > min_radius + 1:
                old_max = max_radius
                max_radius = (min_radius * 0.2 + max_radius * 0.8)
                print 'Shrinking max circle from %f to %f' % (old_max, max_radius)
                continue
            break

        shape.x, shape.y = location[0], location[1]
        
        set_color(shape)
        
        ClearMask(mask, shape)
        shapes.append(shape)
    return shapes

        
def main():
    usage = "usage: %prog [options] input_file output_file"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--min_radius",
                      dest="min_radius", default=1.5,
                      help="Min radius of shapes to use")
    parser.add_option("-x", "--max_radius",
                      dest="max_radius", default=4.5,
                      help="Max radius of shapes to use")
    parser.add_option("-s", "--square", 
                      dest="square", default=False,
                      help="Use squares (instead of circles")
    (options, args) = parser.parse_args()
    print options, args
    if len(args) < 2:
        print usage
        return -1

    image_path = args[0]
    output_path = args[1]
    image = mpimg.imread(image_path)
    width, height = len(image[0]), len(image)
    mask = [[0 for x in xrange(0, width)]
            for y in xrange(0, height)]
    for y in xrange(0, len(mask)):
        for x in xrange(0, len(mask[y])):
            mask[y][x] = image[y][x][0] > 0 or image[y][x][1] > 0 or image[y][x][2] > 0
    
    set_color = lambda x: SetColorFromImage(image, x)
    if options.square:
        generate_shape = lambda n, x: GenerateRandomShape(n, x, class_type=Square)
    else:
        generate_shape = lambda n, x: GenerateRandomShape(n, x, class_type=Circle)
    shapes = FillMaskWithShapes(mask, generate_shape, set_color,
                                options.min_radius, options.max_radius)
    WriteShapes(output_path, shapes, width, height)


if __name__ == '__main__':
    main()
