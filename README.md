# Parallel Loops: Merge Sort

This project implements an **iterative** (bottom-up) merge sort using the provided `OmpLoop` parallel-loop helper. It avoids recursion and matches the “parallel loops” model by operating in passes over run widths 1, 2, 4, and so on. The implementation includes adaptive **coarsening** and **parallel-in-merge** (merge-path) to keep threads busy in early and late passes respectively.

## Repository layout (subset)

```
mergesort_with_loops/
├── params.sh
├── Makefile
├── libgen.a           # common data-generation library
├── gen_lib.c
├── mergesort/
│   ├── Makefile
│   ├── mergesort.cpp  # hybrid iterative parallel mergesort
│   ├── omploop.hpp
│   ├── test.sh
│   ├── bench_mergesort.sh
│   ├── plot.sh        # gnuplot (PDFs)
│   ├── plot_py.py     # Python fallback (PNGs+PDFs)
│   ├── make_submission.py # builds submission PDF
│   └── {result,plots}/
└── sequential/
    ├── Makefile
    ├── mergesort_seq.cpp   # sequential baseline
    ├── bench_sequential.sh
    └── result/
```

## Build prerequisites

- GCC / G++ with OpenMP support
- Bash, `make`
- Either **gnuplot** or **Python 3 + matplotlib + pandas** for plotting

## One-time setup

From project root:
```bash
cd /data/akhalegh/utils/parallel-computing/mergesort_with_loops
make libgen.a
```

## Build and bench

1) **Sequential baseline**
```bash
cd sequential
make
make bench    # writes sequential/result/mergesort_seq_<N>
```

2) **Parallel version**
```bash
cd ../mergesort
make
bash ./test.sh       # functional and timing sanity
make bench           # writes mergesort/result/mergesort_<N>_<T>
```

## Plotting

- **gnuplot path** (produces PDFs):
  ```bash
  make plot   # runs plot.sh -> plots/mergesort_speedup_n.pdf + mergesort_speedup_thread.pdf
  ```

- **Python fallback** (produces PNG + PDF and a CSV table):
  ```bash
  python3 plot_py.py
  # outputs to mergesort/plots/
  #   mergesort_speedup_n.{png,pdf}
  #   mergesort_speedup_thread.{png,pdf}
  #   mergesort_time_vs_threads.{png,pdf}
  #   mergesort_efficiency_vs_threads.{png,pdf}
  #   mergesort_speedup_table.csv
  ```

If you change plot styles, delete old images to force regeneration:
```bash
rm -f plots/*.png plots/*.pdf
python3 plot_py.py
```

## Submission PDF

Create a single PDF with **answers-only first page**, **source code**, and **plots**:
```bash
cd mergesort
python3 make_submission.py
# -> mergesort/submission_mergesort.pdf
```

### What the parallel algorithm does

- **Bottom-up passes:** for `width = 1, 2, 4, ...`, merge adjacent runs into a work buffer, then swap buffers.
- **Early passes (tiny runs):** merged serially to avoid scheduling tiny tasks.
- **Middle passes:** parallelized across merges with **grouping** to coarsen iterations and reduce scheduling overhead.
- **Late passes (few big merges):** parallelized **inside** each merge via **merge-path** output partitioning so all threads have work.

### Tuning knobs (in `mergesort.cpp`)

- `SERIAL_PASS_THRESHOLD` (default 64): increase to avoid threading very small runs.
- `ITER_TARGET_FACTOR` (default 4): increase to coarsen more work per parallel iteration.
- `setGranularity(…)`: try 2, 4, or 8 to reduce OpenMP scheduling overhead when iterations are numerous.

## Interpreting results

- Small `N` can show low or negative speedups due to overheads.
- Large `N` improves, but mergesort is **memory-bandwidth bound** (streams 2 inputs + 1 output each pass), so speedup plateaus as threads contend for DRAM bandwidth.
- Parallelizing inside large merges improves late-pass utilization, but scaling remains limited by memory bandwidth and NUMA.

## Troubleshooting

- **Linker cannot find `../libgen.a`**: run `make libgen.a` in the project root or rely on sub-Makefiles that auto-build it.
- **Permission denied for scripts**: run with `bash ./script.sh`.
- **“No results found” in plotter**: make sure both sequential and parallel benches ran and wrote timing files to their `result/` directories.
- **Very large N (1e9)** requires significant RAM; if not available on your node, run only up to what fits and note the limitation.
