#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SEQ_DIR = BASE / "sequential" / "result"
PAR_DIR = BASE / "mergesort" / "result"
PLOTS_DIR = BASE / "mergesort" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Read sequential times: sequential/result/mergesort_seq_<N>
seq_times = {}
for f in sorted(SEQ_DIR.glob("mergesort_seq_*")):
    try:
        n = int(f.name.split("_")[-1])
    except ValueError:
        continue
    s = f.read_text().strip()
    if s:
        seq_times[n] = float(s.split()[0])

# Read parallel times: mergesort/result/mergesort_<N>_<T>
par_times = {}
for f in sorted(PAR_DIR.glob("mergesort_*_*")):
    parts = f.name.split("_")
    try:
        n = int(parts[1]); t = int(parts[2])
    except Exception:
        continue
    s = f.read_text().strip()
    if s:
        par_times.setdefault(n, {})[t] = float(s.split()[0])

rows = []
for n, tmap in par_times.items():
    seq = seq_times.get(n)
    for t, pt in tmap.items():
        sp = (seq / pt) if (seq is not None and pt and pt > 0) else None
        rows.append({"N": n, "threads": t, "seq_time": seq, "par_time": pt, "speedup": sp})
df = pd.DataFrame(rows)
if df.empty:
    raise SystemExit("No results found. Run both benches first.")

df.sort_values(["N", "threads"], inplace=True)
df.to_csv(PLOTS_DIR / "mergesort_speedup_table.csv", index=False)

def save(fig, stem):
    fig.savefig(PLOTS_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(PLOTS_DIR / f"{stem}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

all_threads = sorted(df["threads"].dropna().unique())

# Plot 1: speedup vs threads for each N (with ideal)
fig1 = plt.figure()
for n, sub in df.groupby("N"):
    sub = sub.sort_values("threads")
    plt.plot(sub["threads"], sub["speedup"], marker="o", label=f"N={n}")
plt.plot(all_threads, all_threads, linestyle="--", label="ideal", alpha=0.5)
plt.xlabel("Threads"); plt.ylabel("Speedup (seq/par)")
plt.title("Merge Sort: Speedup vs Threads")
plt.xticks(all_threads); plt.legend()
save(fig1, "mergesort_speedup_n")

# Plot 2: speedup vs N (log-x) for each thread count
fig2 = plt.figure()
for t, sub in df.groupby("threads"):
    sub = sub.sort_values("N")
    plt.plot(sub["N"], sub["speedup"], marker="o", label=f"threads={t}")
plt.xscale("log")
plt.xlabel("Problem size N (log scale)"); plt.ylabel("Speedup (seq/par)")
plt.title("Merge Sort: Speedup vs Problem Size")
plt.legend()
save(fig2, "mergesort_speedup_thread")

print("Wrote plots and table to:", PLOTS_DIR)
