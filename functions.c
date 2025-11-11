#include <math.h>

float f1(float x, int intensity) {
  int sign = x > 0;
  
  for (int i=0; i< intensity; ++i) {
    x = x*x;
    x = sqrt(x);
  }
  return (sign?1:-1)*x;
}

float f2(float x, int intensity) {
  float realx = f1(x, intensity);
  return realx*realx;
}

float f3(float x, int intensity) {
  return sin(f1(x,intensity));
}

float f4(float x, int intensity) {
  return exp(cos(f1(x,intensity)));
}
