#!/usr/bin/env python3
"""
Create a PDF for the mergesort_with_loops assignment containing only:
 - Plots: generated if missing, then embedded

Output: mergesort/plots.pdf
"""

from pathlib import Path
import textwrap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MS_DIR = ROOT / "mergesort"
SEQ_DIR = ROOT / "sequential" / "result"
PAR_DIR = MS_DIR / "result"
PLOTS_DIR = MS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
SUBMISSION_PDF = MS_DIR / "plots.pdf"

# --------------- plotting helpers ---------------
def build_plots_if_needed():
    png_targets = [
        PLOTS_DIR / "mergesort_speedup_n.png",
        PLOTS_DIR / "mergesort_speedup_thread.png",
        PLOTS_DIR / "mergesort_time_vs_threads.png",
        PLOTS_DIR / "mergesort_efficiency_vs_threads.png",
    ]
    if all(p.exists() for p in png_targets):
        return

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
            eff = (sp / t) if (sp is not None and t > 0) else None
            rows.append({
                "N": n,
                "threads": t,
                "seq_time": seq,
                "par_time": pt,
                "speedup": sp,
                "efficiency": eff,
            })
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("No results found. Run both benches first: sequential and mergesort.")

    df.sort_values(["N", "threads"], inplace=True)
    df.to_csv(PLOTS_DIR / "mergesort_speedup_table.csv", index=False)

    def save(fig, stem):
        fig.savefig(PLOTS_DIR / f"{stem}.pdf", bbox_inches="tight")
        fig.savefig(PLOTS_DIR / f"{stem}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    all_threads = sorted(df["threads"].dropna().unique())

    # Speedup vs threads for each N (NO ideal line; clamp y to 0..4)
    fig1 = plt.figure()
    for n, sub in df.groupby("N"):
        sub = sub.sort_values("threads")
        plt.plot(sub["threads"], sub["speedup"], marker="o", label=f"N={n}")
    plt.xlabel("Threads"); plt.ylabel("Speedup (seq/par)")
    plt.title("Merge Sort: Speedup vs Threads")
    plt.xticks(all_threads)
    plt.ylim(0, 4)
    plt.yticks([0, 1, 2, 3, 4])
    plt.legend()
    save(fig1, "mergesort_speedup_n")

    # Speedup vs N (log-x) for each thread count
    fig2 = plt.figure()
    for t, sub in df.groupby("threads"):
        sub = sub.sort_values("N")
        plt.plot(sub["N"], sub["speedup"], marker="o", label=f"threads={t}")
    plt.xscale("log")
    plt.xlabel("Problem size N (log)")
    plt.ylabel("Speedup (seq/par)")
    plt.title("Merge Sort: Speedup vs Problem Size")
    plt.legend()
    save(fig2, "mergesort_speedup_thread")

    # Absolute time vs threads (per N)
    fig3 = plt.figure()
    for n, sub in df.groupby("N"):
        sub = sub.sort_values("threads")
        plt.plot(sub["threads"], sub["par_time"], marker="o", label=f"N={n}")
    plt.xlabel("Threads"); plt.ylabel("Time (s)")
    plt.title("Merge Sort: Parallel Time vs Threads")
    plt.xticks(all_threads)
    plt.legend()
    save(fig3, "mergesort_time_vs_threads")

    # Efficiency vs threads (per N)
    fig4 = plt.figure()
    for n, sub in df.groupby("N"):
        sub = sub.sort_values("threads")
        plt.plot(sub["threads"], sub["efficiency"], marker="o", label=f"N={n}")
    plt.xlabel("Threads"); plt.ylabel("Parallel Efficiency (speedup per thread)")
    plt.title("Merge Sort: Efficiency vs Threads")
    plt.ylim(0, 1.05)
    plt.xticks(all_threads)
    plt.legend()
    save(fig4, "mergesort_efficiency_vs_threads")

# --------------- plot pages ---------------
def add_image_page(pdf: PdfPages, img_path: Path, title: str):
    if img_path.suffix.lower() == ".png":
        import matplotlib.image as mpimg
        img = mpimg.imread(img_path)
        fig = plt.figure(figsize=(11, 8.5))
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.84])
        ax.imshow(img)
        ax.axis("off")
        fig.suptitle(title, fontsize=12, x=0.08, y=0.97, ha="left")
        pdf.savefig(fig)
        plt.close(fig)
    else:
        fig = plt.figure(figsize=(11, 8.5))
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.84])
        ax.axis("off")
        ax.text(0.02, 0.9, f"{title}", fontsize=14, weight="bold")
        ax.text(0.02, 0.8, f"Plot file: {img_path.name}", fontsize=11)
        ax.text(
            0.02,
            0.7,
            "PNG not found. Please generate PNG plots with the Python plotter.",
            fontsize=10,
        )
        pdf.savefig(fig)
        plt.close(fig)

def main():
    # Ensure plots exist (PNG preferred for embedding)
    build_plots_if_needed()

    png_speedup_n      = PLOTS_DIR / "mergesort_speedup_n.png"
    png_speedup_thread = PLOTS_DIR / "mergesort_speedup_thread.png"
    png_time_vs_t      = PLOTS_DIR / "mergesort_time_vs_threads.png"
    png_eff_vs_t       = PLOTS_DIR / "mergesort_efficiency_vs_threads.png"

    with PdfPages(SUBMISSION_PDF) as pdf:
        # Plot pages only
        add_image_page(pdf, png_speedup_n,      "Speedup vs Threads")
        add_image_page(pdf, png_speedup_thread, "Speedup vs Problem Size (log scale)")
        add_image_page(pdf, png_time_vs_t,      "Parallel Time vs Threads")
        add_image_page(pdf, png_eff_vs_t,       "Parallel Efficiency vs Threads")

    print(f"Wrote {SUBMISSION_PDF}")

if __name__ == "__main__":
    main()
