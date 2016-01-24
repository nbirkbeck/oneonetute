#include <iostream>
#include <math.h>

class Shape {
public:
  Shape(int x, int y) : x_(x), y_(y) {}

  virtual float GetArea() = 0;
  
protected:
  int x_;
  int y_;
};


class Circle : public Shape {
public:
  Circle(int x, int y, float r) : Shape(x, y), r_(r) {}

  float GetArea() {
    return M_PI * r_ * r_;
  }
  
private:
  float r_;

  float data[10000];
};


void SomeOperation(Shape& shape) {
  std::cout << "Area of shape:" << shape.GetArea();
}

int main(int ac, char* av[]) {
  // This should fail...
  // Shape shape(10, 10);
  for (int i = 0; i < 100000000; ++i) {
    Circle* circle = new Circle(10, 10, 10);
  }
  
  return 0;
}
