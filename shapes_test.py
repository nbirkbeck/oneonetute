import math
import unittest
from shapes import Circle


class TestCircle(unittest.TestCase):
    def test_GetArea(self):
        circle = Circle(10, 10, 1)
        self.assertEqual(math.pi, circle.GetArea())

        circle = Circle(20, 20, 1)
        self.assertEqual(math.pi, circle.GetArea())

    def test_IsInside(self):
        circle = Circle(0, 0, 1)
        self.assertTrue(circle.IsInside(0, 0))
        self.assertTrue(circle.IsInside(1, 0))
        self.assertTrue(circle.IsInside(0, 1))
        self.assertFalse(circle.IsInside(0, 1.1))

    # TODO(luke): add more tests (for other shapes and methods)
        
if __name__ == '__main__':
    unittest.main()
