CFLAGS=-O3 -std=c11 -fPIC -g -Xassembler -mrelax-relocations=no
CXXFLAGS=-O3 -std=c++17 -fPIC -g -Xassembler -mrelax-relocations=no
LDFLAGS=-fPIE
LD=g++

all: activity-mergesort.tgz

libgen.a: gen_lib.o
	ar rcs libgen.a gen_lib.o

%.pdf: %.tex
	pdflatex $<

ARXIV=Makefile approx.cpp \
      libgen.a \
      sequential/bench_sequential.sh sequential/Makefile sequential/mergesort_seq.cpp  sequential/queue.sh \
      mergesort/bench_mergesort.sh mergesort/Makefile mergesort/mergesort.cpp mergesort/omploop.hpp mergesort/plot.sh mergesort/queue.sh mergesort/test.sh \
      .gitignore params.sh \
      activity_mergesort_loops.pdf

activity-mergesort.tgz: $(ARXIV)
	tar zcvf $@ \
                 $(ARXIV)

