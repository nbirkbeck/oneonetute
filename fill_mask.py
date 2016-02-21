"""
Application to fill an image mask with some random shapes and
assign the shapes a color based on the input image or some 
specified set of colors.
"""
import math
import utils
from shapes import *
from optparse import OptionParser
import sys
import numpy
import cairo
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from random import random as rand
from scipy.spatial import Delaunay


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


def MeetsOverlapConstraint(shape, mask, min_overlap_ratio=0.97):
    w, h = len(mask[0]), len(mask)
    overlap_area, shape_area = 0.0, 0.0
    for point in shape.InsideRegion(w, h):
        shape_area += 1
        if mask[point[1]][point[0]]:
            overlap_area += 1
    if shape_area <= 0: return False
    return overlap_area / shape_area >= min_overlap_ratio

def FindLocation(mask, shape, start_pos=(0, 0), min_overlap_ratio=0.97, use_first_location=True):
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
    
    for y in xrange(start_pos[1] + int(rand() * 2 - 1), h, 2):
        x_start = start_pos[0] if y == start_pos[1] else 0
        for x in xrange(x_start, w, 2):
            checked += 1
            if mask[y][x]:
                shape.x, shape.y = x, y
                if MeetsOverlapConstraint(shape, mask, min_overlap_ratio):
                    if use_first_location:
                        return (x, y)
                    locations.append((x, y))

    print 'Checked %d locations' % checked
    if locations == []:
        print 'There are no locations'
        return None

    index = int(math.floor(rand() * len(locations)))
    return locations[index]


def ClearMask(mask, shape, padding=0.1):
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
    shape.r -= padding

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
    location = (0, 0)
    for i in xrange(0, 100000):
        shape = generate_shape(min_radius, max_radius)
        location = FindLocation(mask, shape, location)
        if not location:
            if max_radius > min_radius + 1:
                old_max = max_radius
                max_radius = (min_radius * 0.2 + max_radius * 0.8)
                print 'Shrinking max circle from %f to %f' % (old_max, max_radius)
                location = (0, 0)
                continue
            break

        shape.x, shape.y = location[0], location[1]
        
        set_color(shape)
        
        ClearMask(mask, shape)
        shapes.append(shape)
    return shapes

def SmoothPoints(points, neighbors):
    new_points = [[0, 0] for i in xrange(0, len(points))]
    for i in xrange(0, len(points)):
        new_points[i][0] = points[i][0]
        new_points[i][1] = points[i][1]
        for j in neighbors[i]:
            new_points[i][0] += points[j][0]
            new_points[i][1] += points[j][1]
        new_points[i][0] /= (len(neighbors[i]) + 1)
        new_points[i][1] /= (len(neighbors[i]) + 1)
    return new_points

def DelaunayTriangulation(mask, generate_shape, set_color, min_radius, max_radius):
    w, h = len(mask[0]), len(mask)
    npoints = 10000
    points = [(rand() * w, rand() * h) for i in xrange(0, npoints)]
    triangles = Delaunay(points)
    neighbors = [set() for point in points]
    for i in xrange(0, len(triangles.simplices)):
        tri = triangles.simplices[i]
        for k in xrange(0, 3):
            neighbors[tri[k]].add(tri[(k + 1) % 3])
            neighbors[tri[k]].add(tri[(k + 2) % 3])

    for i in xrange(0, 1):
        points = SmoothPoints(points, neighbors)    
    
    shapes = []
    for i in xrange(0, len(neighbors)):
        min_distance = float(w + h)
        for j in neighbors[i]:
            min_distance = min(min_distance,
                               utils.Vec2Distance(points[i], points[j]))
        radius = min_distance / 2
        circle = Circle(points[i][0], points[i][1], radius)
        set_color(circle)
        shapes.append(circle)

    for i in xrange(0, len(neighbors)):
        min_distance = float(w + h)
        for j in neighbors[i]:
            min_distance = min(min_distance,
                               utils.Vec2Distance(points[i], points[j]) - shapes[j].r)
        shapes[i].r = min_distance  - 0.04

    final_shapes = []
    for circle in shapes:
        if MeetsOverlapConstraint(circle, mask):
            final_shapes.append(circle)

    return final_shapes
        
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
    parser.add_option("-t", "--triangle",
                      dest="triangle", default=False,
                      help="Use delaunay triangulation")
                    
    (options, args) = parser.parse_args()
    options.min_radius = float(options.min_radius)
    options.max_radius = float(options.max_radius)
    print options, args
    if len(args) < 2:
        print usage
        return -1

    print 'Reading images'
    image_path = args[0]
    output_path = args[1]
    image = mpimg.imread(image_path)
    width, height = len(image[0]), len(image)
    mask = image[:,:,0] > 0 #+ image[:,:,1] > 0 + image[:,:,2]
    set_color = lambda x: SetColorFromImage(image, x)

    if options.square:
        generate_shape = lambda n, x: GenerateRandomShape(n, x, class_type=Square)
    else:
        generate_shape = lambda n, x: GenerateRandomShape(n, x, class_type=Circle)
        
    if options.triangle:
        print 'Running del'
        shapes = DelaunayTriangulation(mask, generate_shape, set_color,
                                       options.min_radius, options.max_radius)
        for shape in shapes:
            ClearMask(mask, shape)
    else:
        shapes = []
    shapes += FillMaskWithShapes(mask, generate_shape, set_color,
                                 options.min_radius, options.max_radius)
    WriteShapes(output_path, shapes, width, height)


if __name__ == '__main__':
    main()
