"""Make figures and summary tables from results/results.csv. Run: python plot.py"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("results/results.csv")
os.makedirs("results/figs", exist_ok=True)
df["nc"] = df["n"] * df["capacity"]
df["speedup"] = df["t_array"] / df["t_lists"]
df["list_ratio"] = df["avg_list"] / (df["capacity"] + 1)


def loglog_slope(x, y):
    return np.polyfit(np.log(x), np.log(y), 1)[0]


# Fig 1: time vs n*c (E1 + E2 combined), log-log, with fitted slopes
sub = df[df.experiment.isin(["E1_vary_n", "E2_vary_c"])]
g = sub.groupby(["experiment", "n", "capacity"]).agg(
    nc=("nc", "first"), t_lists=("t_lists", "median"), t_array=("t_array", "median")).reset_index()
fig, ax = plt.subplots(figsize=(6, 4.5))
slopes = {}
for col, lab in (("t_lists", "DP-with-Lists"), ("t_array", "DP-1 (array)")):
    ax.loglog(g.nc, g[col], "o", label=lab)
    slopes[lab] = loglog_slope(g.nc, g[col])
    xs = np.sort(g.nc.values)
    k = np.polyfit(np.log(g.nc), np.log(g[col]), 1)
    ax.loglog(xs, np.exp(k[1]) * xs ** k[0], "-", alpha=0.5)
ax.set_xlabel("n * c"); ax.set_ylabel("median time (s)")
ax.set_title("Running time vs n*c (uncorrelated, E1+E2)"); ax.legend(); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig("results/figs/fig1_time_vs_nc.png", dpi=150); plt.close(fig)

# Fig 2: time / (n*c) for each experiment
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (exp, xcol) in zip(axes, (("E1_vary_n", "n"), ("E2_vary_c", "capacity"))):
    s = df[df.experiment == exp].groupby(xcol).agg(
        a=("t_lists", "median"), b=("t_array", "median"), nc=("nc", "median")).reset_index()
    ax.plot(s[xcol], s.a / s.nc * 1e9, "o-", label="DP-with-Lists")
    ax.plot(s[xcol], s.b / s.nc * 1e9, "s-", label="DP-1 (array)")
    ax.set_xscale("log"); ax.set_xlabel(xcol); ax.set_ylabel("ns per (n*c)"); ax.set_title(exp); ax.legend()
fig.tight_layout(); fig.savefig("results/figs/fig2_time_per_nc.png", dpi=150); plt.close(fig)

# Fig 3: speedup by instance type and capacity fraction (E3)
e3 = df[df.experiment == "E3_type_frac"]
s3 = e3.groupby(["kind", "frac_target"]).agg(
    speedup=("speedup", "median"), ratio=("list_ratio", "mean")).reset_index()
fig, ax = plt.subplots(figsize=(7, 4.5))
for kind, d in s3.groupby("kind"):
    ax.plot(d.frac_target * 100, d.speedup, "o-", label=kind)
ax.axhline(1, color="k", ls="--", lw=0.8)
ax.set_xlabel("capacity (% of total weight)"); ax.set_ylabel("speedup = t_array / t_lists")
ax.set_title("Speedup of lists over array DP (>1: lists faster)"); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("results/figs/fig3_speedup_by_type.png", dpi=150); plt.close(fig)

# Fig 4: machine-independent explanation: speedup vs avg|L|/c, all rows
fig, ax = plt.subplots(figsize=(6, 4.5))
for kind, d in df.groupby("kind"):
    ax.scatter(d.list_ratio, d.speedup, s=14, alpha=0.6, label=kind)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("average |L| / (c+1)"); ax.set_ylabel("speedup")
ax.set_title("Speedup vs. list size relative to c"); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig("results/figs/fig4_speedup_vs_listratio.png", dpi=150); plt.close(fig)

# Fig 5: work counts (candidates vs array updates) -- machine independent
fig, ax = plt.subplots(figsize=(6, 4.5))
for kind, d in df.groupby("kind"):
    ax.scatter(d.array_updates, d.candidates, s=14, alpha=0.6, label=kind)
lim = [df.array_updates.min(), df.array_updates.max()]
ax.plot(lim, [2 * x for x in lim], "k--", lw=0.8, label="y = 2x (worst-case bound)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("array DP updates"); ax.set_ylabel("list DP candidates processed")
ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig("results/figs/fig5_work_counts.png", dpi=150); plt.close(fig)

# Fig 6: extremes (E5)
e5 = df[df.experiment == "E5_extremes"].groupby(["kind", "n"]).agg(
    speedup=("speedup", "median"), ratio=("list_ratio", "mean")).reset_index()
fig, ax = plt.subplots(figsize=(6, 4.5))
for kind, d in e5.groupby("kind"):
    ax.plot(d.n, d.speedup, "o-", label=kind)
ax.axhline(1, color="k", ls="--", lw=0.8); ax.set_xscale("log")
ax.set_xlabel("n"); ax.set_ylabel("speedup"); ax.set_title("Worst vs best case for lists (E5)")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("results/figs/fig6_extremes.png", dpi=150); plt.close(fig)

# Tables
with open("results/summary.txt", "w") as f:
    f.write("Fitted log-log slopes of time vs n*c (expect ~1):\n")
    for k, v in slopes.items():
        f.write(f"  {k}: {v:.3f}\n")
    f.write("\nE3: median speedup and mean avg|L|/(c+1) by type and capacity fraction\n")
    f.write(s3.round(3).to_string(index=False) + "\n")
    f.write("\nE5 extremes\n" + e5.round(3).to_string(index=False) + "\n")
    f.write("\nE1/E2 medians\n")
    f.write(df[df.experiment.isin(["E1_vary_n", "E2_vary_c"])].groupby(["experiment", "n", "capacity"]).agg(
        t_lists=("t_lists", "median"), t_array=("t_array", "median"),
        avg_list=("avg_list", "mean"), cand=("candidates", "mean"), upd=("array_updates", "mean")
    ).round(5).to_string() + "\n")
print(open("results/summary.txt").read())
