CFLAGS=-O3 -std=c11 -fPIC -g
CXXFLAGS=-O3 -std=c++17 -fPIC -g -fopenmp -pthread
ARCHIVES=../libgen.a
LD=g++
LDFLAGS=-pthread -fopenmp

all: mergesort

mergesort: mergesort.o $(ARCHIVES)
	$(LD) $(LDFLAGS) mergesort.o $(ARCHIVES) -o mergesort

# Auto-build the parent static lib if missing
$(ARCHIVES):
	$(MAKE) -C .. libgen.a

test: mergesort
	bash ./test.sh

bench: mergesort
	bash ./queue.sh

plot:
	@if command -v gnuplot >/dev/null 2>&1; then \
		bash ./plot.sh; \
	else \
		echo "gnuplot not found; using Python fallback..."; \
		python3 ./plot_py.py; \
	fi

clean:
	-rm *.o
	-rm mergesort

distclean:
	-rm *.out

.PHONY: all mergesort test bench plot clean distclean
