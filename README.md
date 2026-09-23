## OpenMP bottom-up merge sort with merge-path partitioning, scaled to 10⁹ elements on 64 threads

This project implements an iterative, bottom-up merge sort in C++ and parallelizes it with OpenMP. Because the amount and shape of available parallelism change from one pass to the next, the implementation switches strategies as the sort progresses: small early passes run serially, middle passes distribute many independent merges across threads, and late passes split individual large merges across threads using merge-path partitioning. Performance is evaluated against a sequential baseline for problem sizes from 10⁴ to 10⁹ elements and thread counts from 1 to 64.

---

## Key Results

Best observed speedup over the sequential baseline for each problem size:

| N | Best thread count | Speedup | Parallel efficiency |
|---:|---:|---:|---:|
| 10⁴ | 4 | 1.42× | 0.36 |
| 10⁶ | 16 | 2.05× | 0.13 |
| 10⁸ | 64 | 2.85× | 0.04 |
| 10⁹ | 64 | 3.96× | 0.06 |

Speedup grows with problem size, reaching 3.96× at 10⁹ elements and reducing the runtime from 161.7 s (sequential) to roughly 41 s. Scaling is strongly sublinear beyond 4 threads; see [Analysis](#analysis) for the likely causes.

---

## Algorithm

### Bottom-up merge sort

Classic merge sort recursively splits the array and merges on the way back up. The bottom-up variant removes the recursion: it treats every element as a sorted run of length 1 and makes repeated passes over the array, merging adjacent runs and doubling the run width each pass (1, 2, 4, 8, ...) until a single run spans the whole array. A sort of N elements takes ⌈log₂ N⌉ passes, about 30 for N = 10⁹.

The implementation uses two buffers, `src` and `dst`. Each pass reads sorted runs of length `width` from `src`, merges each adjacent pair into a run of length `2 * width` in `dst`, and then swaps the two buffers. This ping-pong scheme avoids allocating temporary storage during the sort.

### Pass-dependent parallelization

Early passes contain a very large number of tiny merges; late passes contain only a few very large ones. No single parallelization strategy fits both, so the implementation selects one of three per pass:

| Regime | Condition | Strategy |
|---|---|---|
| Serial | `width < SERIAL_PASS_THRESHOLD` | Merge sequentially; runs are too short to amortize OpenMP overhead |
| Inter-merge | Many independent merges in the pass | Distribute merges across threads, with several merges coarsened into each loop iteration |
| Intra-merge | Few large merges in the pass | Split each merge across threads using merge-path partitioning |

**Inter-merge parallelism.** For a given pass, the implementation computes `merges_this_pass` and groups several consecutive merges into a single loop iteration. This coarsening reduces the number of iterations the OpenMP scheduler must manage. The groups are then processed in parallel through `OmpLoop::parfor`.

**Intra-merge parallelism with merge path.** When a pass has fewer merges than threads, parallelizing across merges leaves threads idle. Instead, `merge_runs_parallel` divides each merge's output range into tiles that threads process independently.

The key step is `mergepath_partition`. Merging sorted runs `A` and `B` produces an output of length `lenOut = |A| + |B|`. For any output index `K`, the first `K` output elements consist of some prefix `A[0, ia)` and some prefix `B[0, ib)` with `ia + ib = K`. The split point `(ia, ib)` (also called the co-rank of `K`) is found by binary search along the diagonal `ia + ib = K` of the merge grid, in O(log K) time.

Each tile computes the split points for its start and end output indices, then merges its slice of `A` and `B` into its slice of the output. Tiles have equal output lengths regardless of how the input values are distributed, so the load is balanced across threads, and no synchronization is needed between tiles.

### The `OmpLoop` abstraction

`omploop.hpp` wraps OpenMP's parallel loop in a small interface that controls the thread count and granularity:

```cpp
OmpLoop loop;
loop.setNbThread(nbthreads);
loop.setGranularity(1);

loop.parfor(beg, end, increment, [&](int i) {
    // work for iteration i
});
```

---

## Repository Structure

```text
.
├── Makefile                 # Builds libgen.a (shared data-generation library)
├── params.sh                # Benchmark problem sizes and thread counts
├── sequential/
│   ├── Makefile             # Builds mergesort_seq
│   ├── queue.sh             # Sequential benchmark driver
│   └── result/              # Sequential timings: mergesort_seq_<N>
└── mergesort/
    ├── Makefile             # Builds, tests, benchmarks, and plots the parallel sort
    ├── mergesort.cpp        # Parallel bottom-up merge sort
    ├── omploop.hpp          # OmpLoop parallel-for wrapper
    ├── queue.sh             # Parallel benchmark driver
    ├── plot.sh              # gnuplot plotting script
    ├── plot_py.py           # Python plotting fallback
    ├── plots.py             # Full plot set and combined PDF
    ├── result/              # Parallel timings: mergesort_<N>_<T>
    └── plots/               # Generated figures and speedup table
```

---

## Requirements

- C and C++ compilers with OpenMP support (for example, `gcc` and `g++`)
- `make` and `bash`
- For plotting, either `gnuplot` or Python 3 with `matplotlib` and `pandas`

---

## Configuration

Benchmark problem sizes and thread counts are defined in `params.sh`:

```bash
THREADS="1 4 16 64"
MERGESORT_NS="10000 1000000 100000000 1000000000"
```

Edit these values to change the benchmark sweep. The largest configuration sorts 10⁹ elements, so make sure the machine has enough memory for the input array and its second buffer.

---

## Build and Run

### 1. Build the data-generation library

From the project root:

```bash
make libgen.a
```

The sub-project Makefiles build `libgen.a` automatically if it is missing.

### 2. Run the sequential baseline

```bash
cd sequential
make          # builds mergesort_seq
make bench    # equivalent to: bash ./queue.sh
```

Each problem size writes its runtime in seconds to `sequential/result/mergesort_seq_<N>`.

### 3. Run the parallel sort

```bash
cd ../mergesort
make          # builds the OpenMP merge sort
make test     # functional and timing-format tests
make bench    # equivalent to: bash ./queue.sh
```

Each configuration writes its runtime in seconds to `mergesort/result/mergesort_<N>_<T>`, where `T` is the thread count.

### 4. Generate plots

Both benchmarks must be completed first.

```bash
cd mergesort
make plot
```

`make plot` uses `gnuplot` through `plot.sh` when available, and otherwise falls back to `python3 plot_py.py`. Either path produces:

- `plots/mergesort_speedup_n.{pdf,png}`
- `plots/mergesort_speedup_thread.{pdf,png}`
- `plots/mergesort_speedup_table.csv` (Python path)

For the complete figure set and a combined PDF:

```bash
python3 plots.py
```

This additionally produces `plots/mergesort_time_vs_threads.{pdf,png}`, `plots/mergesort_efficiency_vs_threads.{pdf,png}`, and `submission_mergesort.pdf`.

---

## Metrics

With $t_{\text{seq}}(N)$ the sequential runtime and $t_{\text{par}}(N, T)$ the parallel runtime on $T$ threads:

$$
\text{speedup}(N, T) = \frac{t_{\text{seq}}(N)}{t_{\text{par}}(N, T)}
\qquad
\text{efficiency}(N, T) = \frac{\text{speedup}(N, T)}{T}
$$

The full dataset is in `mergesort/plots/mergesort_speedup_table.csv`, with columns `N`, `threads`, `seq_time`, `par_time`, `speedup`, and `efficiency`.

---

## Results

### Sequential baseline

| N | Runtime (s) |
|---:|---:|
| 10⁶ | 0.0938 |
| 10⁸ | 11.99 |
| 10⁹ | 161.66 |

### Thread scaling at N = 10⁸

| Threads | Runtime (s) | Speedup | Efficiency |
|---:|---:|---:|---:|
| 1 | 11.26 | 1.07× | 1.07 |
| 4 | 5.52 | 2.17× | 0.54 |
| 16 | 4.38 | 2.74× | 0.17 |
| 64 | 4.20 | 2.85× | 0.04 |

The parallel implementation on one thread is about 6% faster than the sequential baseline. Going from 1 to 4 threads roughly halves the runtime, while going from 16 to 64 threads improves it by only about 4%.

### Plots

**Speedup vs. thread count, for each N**

![Speedup vs. thread count](mergesort/plots/mergesort_speedup_n.png)

**Speedup vs. problem size, for each thread count** (logarithmic x-axis)

![Speedup vs. problem size](mergesort/plots/mergesort_speedup_thread.png)

**Parallel runtime vs. thread count**

![Parallel runtime vs. thread count](mergesort/plots/mergesort_time_vs_threads.png)

**Parallel efficiency vs. thread count**

![Parallel efficiency vs. thread count](mergesort/plots/mergesort_efficiency_vs_threads.png)

---

## Analysis

**Small inputs.** At N = 10⁴, the whole sort takes only microseconds, so thread startup and scheduling overhead outweigh the parallel work. The best result, 1.42× on 4 threads, reflects how little work there is to distribute.

**Larger inputs.** Speedup rises with problem size, from 2.05× at 10⁶ to 3.96× at 10⁹, because larger inputs give each thread more work relative to fixed overheads.

**Sublinear scaling.** Efficiency drops sharply beyond 4 threads, and adding threads beyond 16 yields little improvement. Two factors are likely responsible:

- **Memory bandwidth.** Merging performs very little computation per element: each pass streams the entire array from `src` and writes it to `dst`. Once enough threads are active to saturate DRAM bandwidth, additional threads cannot make the passes faster.
- **Serial early passes.** Every pass with `width < SERIAL_PASS_THRESHOLD` processes all N elements on a single thread. By Amdahl's law, these passes set an upper bound on speedup that grows more restrictive as the thread count increases.

---

## Possible Improvements

- **Parallelize the early passes.** Sorting fixed-size blocks independently on each thread (for example, with insertion sort or a per-thread bottom-up sort) before the global passes would remove the serial fraction.
- **Reduce memory traffic.** Merging more than two runs at a time (multiway merging) reduces the number of passes over the array, and therefore the total data moved through memory.
- **Thread placement.** On multi-socket systems, pinning threads and allocating memory with NUMA awareness can improve effective bandwidth.

---

## Limitations

- **Hardware not reported.** Speedup at high thread counts depends heavily on the number of physical cores, simultaneous multithreading, memory channels, and NUMA topology. Results measured with 64 threads are only fully interpretable alongside these details.
- **Single-run timings.** Each configuration is timed once. Repeating runs and reporting the median would reduce the effect of system noise, particularly at small problem sizes.
