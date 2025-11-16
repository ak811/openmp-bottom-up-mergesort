# Parallel Merge Sort: Parallelization Study

This project implements and analyzes a **parallel bottom up mergesort** using OpenMP.

Goals:

- Implement a **sequential baseline** for mergesort.
- Implement a **parallel iterative mergesort** that uses the `OmpLoop` helper.
- Measure speedup for different input sizes and thread counts.
- Visualize results using the plots in `mergesort/plots/`.

The parallel implementation uses:

- Iterative bottom up mergesort (run widths 1, 2, 4, 8, ...).
- Parallelism across independent merges when there are many merges in a pass.
- Parallelism inside a single merge using a merge path style partitioning when there are only a few large merges.
- Coarsening of loop iterations to reduce OpenMP scheduling overhead.

---

## Repository Layout

```text
mergesort-parallelization-study/
├── Makefile                 top level build (libgen + tarball)
├── params.sh                common benchmark parameters
├── functions.c              functions for numerical integration (other assignment)
├── gen_lib.c                data generation and result checking
├── gen_lib.o, libgen.a      compiled and static library
├── approx.cpp               helper to compare floating point values
├── sequential_lib.c         sequential integration library (other assignment)
├── README.md                this file
│
├── sequential/              sequential mergesort baseline
│   ├── Makefile
│   ├── mergesort_seq.cpp    recursive sequential mergesort
│   ├── mergesort_seq        executable
│   ├── bench_sequential.sh  run sequential benchmarks
│   ├── queue.sh             wrapper to run locally
│   └── result/
│       ├── mergesort_seq_10000
│       ├── mergesort_seq_1000000
│       ├── mergesort_seq_100000000
│       └── mergesort_seq_1000000000
│
└── mergesort/               parallel bottom up mergesort
    ├── Makefile
    ├── omploop.hpp          OpenMP based parallel loop abstraction
    ├── mergesort.cpp        core parallel iterative mergesort
    ├── mergesort            executable
    ├── bench_mergesort.sh   run parallel benchmarks
    ├── queue.sh             wrapper to run locally
    ├── test.sh              correctness and timing sanity checks
    │
    ├── plot.sh              gnuplot based plotting (PDF)
    ├── plot_py.py           Python plotting (speedup plots + CSV)
    ├── plots.py             creates submission PDF with all plots
    │
    ├── result/              raw timing results
    │   ├── mergesort_<N>_<T>              parallel times
    │   ├── speedup_mergesort_<N>          speedup vs threads
    │   └── speedup_mergesort_thread_<T>   speedup vs N
    │
    ├── plots/               generated plots and summary table
    │   ├── mergesort_speedup_n.pdf
    │   ├── mergesort_speedup_thread.pdf
    │   ├── mergesort_time_vs_threads.pdf
    │   ├── mergesort_efficiency_vs_threads.pdf
    │   └── mergesort_speedup_table.csv
    │
    └── submission_mergesort.pdf           compact PDF with plots only
```

---

## Build Prerequisites

- C and C++ compiler with OpenMP support (for example `gcc` and `g++`)
- `make` and `bash`
- For plotting:
  - either `gnuplot`
  - or Python 3 with `matplotlib` and `pandas`

---

## Parameters

Common benchmark parameters are defined in `params.sh`:

```bash
THREADS="1 4 16 64"
MERGESORT_NS="10000 1000000 100000000 1000000000"
```

These control the problem sizes and thread counts used by the benchmark scripts.

---

## Building and Running

### 1. Build the shared data library (optional but recommended)

From the project root:

```bash
make libgen.a
```

Sub makefiles will auto build `libgen.a` if it is missing, but running it once at the top level is convenient.

---

### 2. Sequential baseline

```bash
cd sequential
make              # builds mergesort_seq
make bench        # or: bash ./queue.sh
```

This writes one timing file per problem size:

```text
sequential/result/mergesort_seq_<N>
```

Each file contains the runtime in seconds on standard error, captured into a file.

Example from this project:

```text
mergesort_seq_1000000    ->  0.0937723
mergesort_seq_100000000  ->  11.9921
mergesort_seq_1000000000 ->  161.663
```

---

### 3. Parallel mergesort

```bash
cd ../mergesort
make              # builds mergesort with OpenMP
make test         # functional and timing format tests
make bench        # or: bash ./queue.sh
```

This produces files of the form:

```text
mergesort/result/mergesort_<N>_<T>
```

Example lines from this project:

```text
mergesort_100000000_1   -> 11.2595
mergesort_100000000_4   -> 5.51965
mergesort_100000000_16  -> 4.38349
mergesort_100000000_64  -> 4.20281
```

---

## Plotting

You must run the sequential and parallel benchmarks first.

### Option A: gnuplot path

```bash
cd mergesort
make plot          # invokes plot.sh
```

This creates PDF plots:

- `plots/mergesort_speedup_n.pdf`
- `plots/mergesort_speedup_thread.pdf`

### Option B: Python plotting path

If `gnuplot` is not available, `make plot` falls back to the Python script:

```bash
python3 plot_py.py
```

This produces:

- `plots/mergesort_speedup_n.pdf` and `.png`
- `plots/mergesort_speedup_thread.pdf` and `.png`
- `plots/mergesort_speedup_table.csv`

For a richer set of plots and a combined submission PDF, run:

```bash
cd mergesort
python3 plots.py
```

This ensures PNG images exist and then writes:

- `plots/mergesort_speedup_n.{pdf,png}`
- `plots/mergesort_speedup_thread.{pdf,png}`
- `plots/mergesort_time_vs_threads.{pdf,png}`
- `plots/mergesort_efficiency_vs_threads.{pdf,png}`
- `submission_mergesort.pdf`

---

## Plots in `mergesort/plots`

After running `plot_py.py` or `plots.py`, you can view the plots directly in the repo.

### 1. Speedup vs threads

File: `mergesort/plots/mergesort_speedup_n.png`

This plot shows, for each fixed `N`, the speedup

\[
	ext{speedup}(N,T) = rac{T_{	ext{seq}}(N)}{T_{	ext{par}}(N,T)}
\]

as a function of thread count `T`.

Small `N` has limited speedup, while large `N` shows better scaling.

---

### 2. Speedup vs problem size

File: `mergesort/plots/mergesort_speedup_thread.png`

This plot shows, for each fixed thread count `T`, how speedup changes as `N` grows. The x axis is logarithmic. As `N` increases, parallel overhead is amortized and speedup improves until memory bandwidth becomes the limiting factor.

---

### 3. Parallel time vs threads

File: `mergesort/plots/mergesort_time_vs_threads.png`

This plot shows the parallel runtime for each `N` as a function of thread count. It helps visualize where adding more threads continues to reduce time, and where additional threads no longer help much.

---

### 4. Parallel efficiency vs threads

File: `mergesort/plots/mergesort_efficiency_vs_threads.png`

Parallel efficiency is defined as:

\[
	ext{efficiency}(N,T) = rac{	ext{speedup}(N,T)}{T}
\]

This indicates how effectively the algorithm uses additional threads. Efficiency is highest for moderate thread counts and drops significantly at very large thread counts where memory bandwidth dominates.

---

## How the Parallel Algorithm Works

The parallel mergesort in `mergesort.cpp` is iterative and uses two buffers `src` and `dst`.

1. **Bottom up passes**

   For `width` equal to 1, 2, 4, 8, and so on:

   - Consider blocks of size `2 * width` in `src`.
   - Treat the left half and right half as sorted runs.
   - Merge them into `dst`.
   - After each pass, swap `src` and `dst`.

2. **Early passes: serial**

   For very small run widths, merging is done serially. The variable `SERIAL_PASS_THRESHOLD` controls when to stop doing fully serial passes. At small widths, the work per merge is tiny and parallel overhead is not worth it.

3. **Middle passes: parallel across merges**

   When there are many independent merges in a pass, the code parallelizes across them. It computes:

   - `merges_this_pass` which is roughly `ceil(n / (2 * width))`
   - A `group` size that coarsens several merges into one parallel iteration.
   - An outer increment `outer_inc` equal to `step * group` where `step = 2 * width`.

   `OmpLoop::parfor` is then used to process groups of merges in parallel. This keeps the number of OpenMP iterations manageable and reduces scheduling overhead.

4. **Late passes: parallel inside each merge**

   If there are only a few large merges in a pass, parallelizing across merges is not enough to keep all threads busy. In that case, the code uses `merge_runs_parallel`, which performs a merge path style partition of the merge output range.

   Idea:

   - Suppose we merge two sorted arrays `A` and `B` into an output of length `lenOut`.
   - For an output index `K` in `[0, lenOut)`, there is a unique pair `(ia, ib)` such that `ia + ib = K` and the elements before those positions in `A` and `B` are less than or equal to the element at output index `K`.
   - `mergepath_partition` finds this pair using a binary search.
   - The output interval is split into tiles, and each tile is merged independently by a chunk of threads.

   This allows many threads to work inside a single large merge.

5. **OmpLoop abstraction**

   `omploop.hpp` wraps OpenMP into a simple interface:

   ```cpp
   OmpLoop loop;
   loop.setNbThread(nbthreads);
   loop.setGranularity(1);

   loop.parfor(beg, end, increment, [&](int i) {
       // do work at i
   });
   ```

   Internally it uses a `#pragma omp parallel` region with a `#pragma omp for` loop and dynamic scheduling.

---

## Speedup Results: Sequential vs Parallel

The combined timing and speedup data are stored in:

```text
mergesort/plots/mergesort_speedup_table.csv
```

Each row contains:

- `N` (problem size)
- `threads`
- `seq_time`
- `par_time`
- `speedup = seq_time / par_time`
- `efficiency = speedup / threads`

From the current data, the best observed speedup for each problem size is:

| N             | Threads with best speedup | Best speedup (approximate) |
|--------------:|--------------------------:|----------------------------:|
| 10,000        | 4                         | 1.42 x                      |
| 1,000,000     | 16                        | 2.05 x                      |
| 100,000,000   | 64                        | 2.85 x                      |
| 1,000,000,000 | 64                        | 3.96 x                      |

### Interpretation by problem size

**N = 10,000**

- Best configuration: 4 threads, speedup about 1.4 x.
- At 16 and 64 threads, the parallel code becomes slower than sequential.
- Reason: overhead from thread management and scheduling is large relative to the amount of work. This is a classic case where parallelization does not pay off for very small problems.

**N = 1,000,000**

- Best configuration: 16 threads, speedup about 2.05 x.
- 4 threads also help (around 1.79 x).
- 64 threads are slightly worse than 16 threads.
- Here there is enough work to benefit from parallelism, but the algorithm is still limited by overhead and memory effects when thread count becomes very large.

**N = 100,000,000**

- Best configuration: 64 threads, speedup about 2.85 x.
- 4 and 16 threads give speedups about 2.17 x and 2.74 x.
- Mergesort becomes strongly memory bound at this scale. Each pass reads two arrays and writes one array, which pushes memory bandwidth. Adding more threads contends on memory and scaling becomes sub linear.

**N = 1,000,000,000**

- Best configuration: 64 threads, speedup about 3.96 x.
- 4 threads: about 2.76 x speedup.
- 16 threads: about 3.65 x speedup.
- This is the largest problem size in the study. There is enough work to amortize overhead, and the parallel algorithm delivers a noticeable speedup. However, even with 64 threads the speedup stays below 4 x, which clearly shows that memory bandwidth and non parallelizable work cap the scaling.

### Parallel efficiency

Efficiency is speedup divided by thread count.

Example values:

- `N = 1,000,000`, `T = 4`  
  speedup about 1.79 x  
  efficiency about 0.45

- `N = 1,000,000,000`, `T = 4`  
  speedup about 2.76 x  
  efficiency about 0.69

- `N = 1,000,000,000`, `T = 64`  
  speedup about 3.96 x  
  efficiency about 0.06

This shows:

- A small number of threads can be used quite efficiently.
- Beyond a certain number of threads, additional cores do not translate into proportional speedup due to bandwidth and overhead.

---


