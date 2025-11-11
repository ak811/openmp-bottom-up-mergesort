#ifndef __OMPLOOP__
#define __OMPLOOP__

#include <functional>

// That does not solve the static activity, but provide the same feature so it can be used as a replacement.
// You need to add -fopenmp to CXXFLAGS and LDFLAGS for this to work.
// set number of thread by called setNbThread.
class OmpLoop {

  int nbthread;
  int granularity;

public:

  OmpLoop()
    :nbthread(1), granularity(1)
  {}
  
  void setNbThread(int t) {
    nbthread = t;
  }

  void setGranularity(int g) {
    granularity = g;
  }


  void parfor (size_t beg, size_t end, size_t increment,
               std::function<void(int)> f
               ) {
#pragma omp parallel num_threads(nbthread)
    {
#pragma omp for schedule(dynamic, granularity) 
      for (size_t i=beg; i<end; i+= increment) {
	f(i);
      }
    }
  }

  
  template<typename TLS>
  void parfor (size_t beg, size_t end, size_t increment,
               std::function<void(TLS&)> before,
               std::function<void(int, TLS&)> f,
               std::function<void(TLS&)> after
               ) {
#pragma omp parallel num_threads(nbthread)
    {
      TLS tls;
      before(tls);
      
#pragma omp for schedule(dynamic, granularity) 
      for (size_t i=beg; i<end; i+= increment) {
	f(i, tls);
      }
#pragma omp critical
      after(tls);
    }
  }

};

#endif
