#include <stdio.h>
#include <iostream>
#include <algorithm>
#include <chrono>
#include "omploop.hpp"

#ifdef __cplusplus
extern "C" {
#endif
  void generateMergeSortData (int* arr, size_t n);
  void checkMergeSortResult (int* arr, size_t n);
#ifdef __cplusplus
}
#endif

// Merge two sorted runs src[l..mid-1] and src[mid..r-1] into dst[l..r-1]
static inline void merge_runs(const int* src, int* dst,
                              size_t l, size_t mid, size_t r) {
  if (l >= r) return;
  if (mid > r) mid = r;

  size_t i = l;
  size_t j = mid;
  size_t k = l;

  // If the right run is empty, just copy left
  if (mid <= l) {
    while (i < r) dst[k++] = src[i++];
    return;
  }

  while (i < mid && j < r) {
    if (src[i] <= src[j]) dst[k++] = src[i++];
    else                  dst[k++] = src[j++];
  }
  while (i < mid) dst[k++] = src[i++];
  while (j < r)   dst[k++] = src[j++];
}

int main (int argc, char* argv[]) {
  if (argc < 3) {
    std::cerr<<"Usage: "<<argv[0]<<" <n> <nbthreads>"<<std::endl;
    return -1;
  }

  const size_t n = static_cast<size_t>(std::max(0, atoi(argv[1])));
  const int nbthreads = std::max(1, atoi(argv[2]));

  int *a = new int[n];
  generateMergeSortData(a, n);

  // Workspace buffer; we'll ping-pong between a and b per pass
  int *b = new int[n];

  OmpLoop loop;
  loop.setNbThread(nbthreads);
  loop.setGranularity(1); // OpenMP chunk size in dynamic schedule

  auto t0 = std::chrono::high_resolution_clock::now();

  // Bottom-up merge sort: pass width = 1,2,4,...
  int *src = a;
  int *dst = b;
  for (size_t width = 1; width < n; width <<= 1) {
    const size_t step = (width << 1);

    // Each iteration merges a pair of runs [i, i+width) and [i+width, i+2*width)
    loop.parfor(0, n, step, [&](int start) {
      size_t i = static_cast<size_t>(start);
      size_t l = i;
      size_t mid = std::min(l + width, n);
      size_t r = std::min(l + step,  n);
      merge_runs(src, dst, l, mid, r);
    });

    // Swap roles for next pass
    std::swap(src, dst);
  }

  // If the last swap left the sorted data in 'b', copy it back to 'a'
  if (src != a) {
    std::copy(src, src + n, a);
  }

  auto t1 = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> elapsed = t1 - t0;
  std::cerr << elapsed.count() << std::endl; // time to stderr

  checkMergeSortResult(a, n);

  delete[] a;
  delete[] b;
  return 0;
}
