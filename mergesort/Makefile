CFLAGS=-O3 -std=c11 -fPIC -g 
CXXFLAGS=-O3 -std=c++17 -fPIC -g -fopenmp -pthread
ARCHIVES=../libgen.a
LD=g++
LDFLAGS=-pthread -fopenmp

all: mergesort 


mergesort: mergesort.o
	$(LD) $(LDFLAGS) mergesort.o $(ARCHIVES) -o mergesort

test: mergesort
	./test.sh

bench: mergesort
	./queue.sh

plot:  
	./plot.sh

clean:
	-rm *.o
	-rm mergesort

distclean:
	rm *.out


.PHONY:  mergesort
