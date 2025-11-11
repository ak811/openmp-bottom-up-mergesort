#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

float f1(float x, int intensity);
float f2(float x, int intensity);
float f3(float x, int intensity);
float f4(float x, int intensity);

#ifdef __cplusplus
}
#endif

  
float sequential_integrate (int argc, char* argv[]) {
  
  int functionid = atoi(argv[1]);
  float a = atof(argv[2]);
  float b = atof(argv[3]);
  int n = atoi(argv[4]);
  int intensity = atoi(argv[5]);

  float (*f) (float, int);
  f = NULL;
  
  if (functionid == 1) {
    f = f1;
  }
  if (functionid == 2) {
    f = f2;
  }
  if (functionid == 3) {
    f = f3;
  }
  if (functionid == 4) {
    f = f4;
  }

  double sum = 0;
  
  for (int i=0; i<n; ++i) {
    float x = a+(i+.5)*(b-a)/n;
    float val = f(x, intensity);

    sum += val;
  }
  float integrate = sum * (b-a)/n;

  return integrate;
}
