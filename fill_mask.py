import math
import shapes
import numpy
import cairo


def main():
    surface = cairo.SVGSurface('/tmp/a.svg', 256, 256)
    ctx = cairo.Context(surface)        
    circle = shapes.Circle(128, 128, 100, [1, 0, 0])
    circle.Draw(ctx)
    print circle
    surface.flush()
    surface.finish()
    
if __name__ == '__main__':
    main()
