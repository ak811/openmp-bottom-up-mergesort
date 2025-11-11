CFLAGS=-O3 -std=c11 -fPIC -g
CXXFLAGS=-O3 -std=c++17 -fPIC -g
ARCHIVES=../libgen.a 
LD=g++


all: mergesort_seq


mergesort_seq: mergesort_seq.o
	$(LD) $(LDFLAGS) mergesort_seq.o $(ARCHIVES) -o mergesort_seq


bench: mergesort_seq
	./queue.sh

clean:
	-rm *.o
	-rm mergesort_seq

distclean:
	-rm *.sh.*

.PHONY:  mergesort_seq
