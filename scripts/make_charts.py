#!/usr/bin/env python3
"""Render the charts and the README banner from results/*.csv.

Usage:  python scripts/make_charts.py
Output: charts/*.png
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "results", ROOT / "charts"
OUT.mkdir(exist_ok=True)

# ---------- look & feel ------------------------------------------------------
BG, PANEL, GRID = "#0B1020", "#141B35", "#232C4D"
TEXT, MUTED = "#EEF1FB", "#8F9BC4"
TEAL, AMBER, VIOLET = "#2DD4BF", "#FBBF24", "#C084FC"
BLUE, CORAL = "#60A5FA", "#FB7185"
FOOT = "github.com/zxb-08/local-llm-cyber-benchmark  ·  RTX 4050 Laptop 6 GB  ·  Ollama"

MODELS = [  # key, display name, colour
    ("qwen3-4b-instruct", "Qwen3 4B Instruct", TEAL),
    ("qwen3-8b", "Qwen3 8B", AMBER),
    ("cyber-8b", "Foundation-Sec 8B", VIOLET),
]
MCOL = {k: c for k, _, c in MODELS}
MNAME = {k: n for k, n, _ in MODELS}

mpl.rcParams.update({
    "font.family": ["Poppins", "DejaVu Sans"],
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": TEXT, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.spines.bottom": False,
})
DPI = 200

speed = pd.read_csv(RES / "speed.csv")
scores = pd.read_csv(RES / "scores.csv")

PROMPTS = ["G1", "G2", "G3", "C1", "C2", "C3", "C4", "P1", "P2", "P3"]
PLABEL = {
    "G1": "Explain a fridge (≤100 words)", "G2": "Train arrival time", "G3": "3-sentence email",
    "C1": "Windows Event ID 4625", "C2": "MITRE ATT&CK mapping", "C3": "Unpublished CVE (hallucination)",
    "C4": "Phishing email", "P1": "Windows log triage", "P2": "Linux log triage", "P3": "Splunk SPL query",
}
GROUPS = [("General", ["G1", "G2", "G3"]), ("Cyber knowledge", ["C1", "C2", "C3", "C4"]),
          ("Practical", ["P1", "P2", "P3"])]


def header(fig, title, subtitle):
    fig.text(0.045, 0.945, title, fontsize=21, fontweight="bold", color=TEXT, va="top")
    fig.text(0.045, 0.885, subtitle, fontsize=10.5, color=MUTED, va="top")
    fig.text(0.045, 0.018, FOOT, fontsize=7.5, color="#5B6794", va="bottom")


def rrect(ax, x, y, w, h, fc, r_px=8, ec="none", lw=0, z=2, alpha=1.0, clip=True):
    """Rounded rectangle whose corner radius is constant in *pixels* on any axes."""
    fig = ax.figure
    pos = ax.get_position()
    ax_w, ax_h = pos.width * fig.get_figwidth() * DPI, pos.height * fig.get_figheight() * DPI
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    xpp, ypp = abs(x1 - x0) / ax_w, abs(y1 - y0) / ax_h
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r_px * xpp}",
                       mutation_aspect=ypp / xpp, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha)
    p.set_clip_on(clip)
    ax.add_patch(p)
    return p


def dot(fig, x, y, color, r=0.0065):
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none"); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ar = fig.get_figwidth() / fig.get_figheight()
    ax.add_patch(plt.matplotlib.patches.Ellipse((x, y), 2 * r, 2 * r * ar, fc=color, ec="none"))


# ---------- 1. speed ---------------------------------------------------------
def chart_speed():
    fig = plt.figure(figsize=(10, 5.4), dpi=DPI)
    header(fig, "Generation speed", "Mean tokens per second over the prompt set · dots are the individual prompts")
    ax = fig.add_axes([0.25, 0.15, 0.68, 0.62])
    ax.set_xlim(0, 75); ax.set_ylim(3.0, -0.2)
    ax.set_yticks([]); ax.set_xticks([0, 20, 40, 60])
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0); ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0, labelsize=9, pad=8)
    ax.set_xlabel("tokens / second", fontsize=9, labelpad=10)
    info = {"qwen3-4b-instruct": "2.9 GB · 100% GPU", "qwen3-8b": "5.7 GB · 73% GPU",
            "cyber-8b": "5.4 GB · 78% GPU"}
    means = {}
    for i, (k, name, col) in enumerate(MODELS):
        v = speed[speed.model == k].eval_rate_tok_s.dropna()
        means[k] = v.mean()
        y = i + 0.5
        rrect(ax, 0, y - 0.19, 75, 0.38, PANEL, r_px=10, z=1)
        rrect(ax, 0, y - 0.19, v.mean(), 0.38, col, r_px=10, z=2)
        ax.scatter(v, [y + 0.34] * len(v), s=9, color=col, alpha=0.5, lw=0, zorder=4)
        fig.text(0.235, 0.77 - (i + 0.5) / 3.2 * 0.62 + 0.012, name, ha="right", fontsize=11.5,
                 fontweight="bold", color=TEXT, va="center")
        fig.text(0.235, 0.77 - (i + 0.5) / 3.2 * 0.62 - 0.03, info[k], ha="right", fontsize=8.2,
                 color=MUTED, va="center")
        xlab = v.mean() - 1.5 if v.mean() > 40 else v.mean() + 1.8
        ax.text(xlab, y, f"{v.mean():.1f}", fontsize=15, fontweight="bold", va="center",
                ha="right" if v.mean() > 40 else "left", color=BG if v.mean() > 40 else col, zorder=5)
    ratio = means["qwen3-4b-instruct"] / means["qwen3-8b"]
    fig.text(0.93, 0.95, f"{ratio:.1f}× faster", ha="right", va="top", fontsize=22, fontweight="bold", color=TEAL)
    fig.text(0.93, 0.885, "Qwen3 4B Instruct vs Qwen3 8B", ha="right", va="top", fontsize=9, color=MUTED)
    fig.savefig(OUT / "01-speed.png", dpi=DPI)
    plt.close(fig)


# ---------- 2. score heat-map ------------------------------------------------
def chart_heatmap():
    cmap = LinearSegmentedColormap.from_list("s", [(0, "#F43F5E"), (0.2, "#FB923C"), (0.4, "#FBBF24"), (0.6, "#86E3A6"), (0.8, "#34D399"), (1, "#2DD4BF")])
    piv = scores.pivot(index="prompt", columns="model", values="score_0_5")
    rows = []
    y = 0.0
    for g, ps in GROUPS:
        rows.append(("hdr", g, y)); y += 0.62
        for p in ps:
            rows.append(("row", p, y)); y += 0.62
        y += 0.18
    avg_y = y + 0.1
    fig = plt.figure(figsize=(10, 8.4), dpi=DPI)
    header(fig, "Score by prompt", "Final answer judged against the ground truth · 0 = wrong or no answer, 5 = fully correct")
    ax = fig.add_axes([0.04, 0.05, 0.92, 0.77])
    ax.set_xlim(-3.55, 2.6); ax.set_ylim(avg_y + 1.0, -0.8); ax.axis("off")
    cx = [-0.55, 0.52, 1.59]
    for (k, name, col), x in zip(MODELS, cx):
        ax.text(x + 0.5, -0.55, name, ha="center", va="center", fontsize=10, fontweight="bold", color=col)
        ax.plot([x + 0.12, x + 0.88], [-0.28, -0.28], color=col, lw=2.2, solid_capstyle="round")
    for kind, key, y in rows:
        if kind == "hdr":
            ax.text(-3.45, y + 0.3, key.upper(), fontsize=7.8, fontweight="bold", color="#6E7BA8", va="center")
            continue
        ax.text(-2.9, y + 0.28, PLABEL[key], ha="left", va="center", fontsize=9.6, color=TEXT)
        ax.text(-3.45, y + 0.28, key, ha="left", va="center", fontsize=9, color=MUTED, fontweight="bold")
        for (k, _, _), x in zip(MODELS, cx):
            s = piv.loc[key, k]
            fc = cmap(s / 5)
            rrect(ax, x, y, 1.0, 0.54, fc, r_px=9)
            ax.text(x + 0.5, y + 0.29, f"{int(s)}", ha="center", va="center", fontsize=12.5,
                    fontweight="bold", color="#0B1020" if s >= 1 else "#FFE4E8")
    # average row
    ax.plot([-3.45, 2.55], [avg_y - 0.15, avg_y - 0.15], color=GRID, lw=1)
    ax.text(-3.45, avg_y + 0.42, "Average (10 prompts)", ha="left", va="center", fontsize=10.5, fontweight="bold")
    for (k, _, col), x in zip(MODELS, cx):
        m = piv[k].mean()
        rrect(ax, x, avg_y + 0.05, 1.0, 0.74, cmap(m / 5), r_px=11, ec="white", lw=1.4)
        ax.text(x + 0.5, avg_y + 0.45, f"{m:.1f}", ha="center", va="center", fontsize=16, fontweight="bold", color="#0B1020")
    # note for the P3 loop
    py = [y for kd, kk, y in rows if kk == "P3"][0]
    ax.text(cx[2] + 0.5, py + 0.505, "", fontsize=1)
    fig.savefig(OUT / "02-score-heatmap.png", dpi=DPI)
    plt.close(fig)


# ---------- 3. category scores ----------------------------------------------
def chart_categories():
    sc = scores.copy()
    cats = [("General", "general"), ("Cyber knowledge", "cyber"), ("Practical", "practical"), ("Overall", None)]
    fig = plt.figure(figsize=(10, 5.6), dpi=DPI)
    header(fig, "Average score by category", "Mean of the per-prompt scores (0–5) · general = 3 prompts, cyber knowledge = 4, practical = 3")
    ax = fig.add_axes([0.07, 0.12, 0.9, 0.63])
    ax.set_xlim(-0.6, 3.6); ax.set_ylim(0, 5.5)
    ax.set_xticks(range(4)); ax.set_xticklabels([c[0] for c in cats], fontsize=10.5, color=TEXT, fontweight="medium")
    ax.set_yticks([0, 1, 2, 3, 4, 5]); ax.tick_params(length=0, labelsize=9, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    bw, gap = 0.235, 0.265
    for j, (k, name, col) in enumerate(MODELS):
        for i, (_, c) in enumerate(cats):
            sub = sc[sc.model == k] if c is None else sc[(sc.model == k) & (sc.category == c)]
            v = sub.score_0_5.mean()
            x = i + (j - 1) * gap - bw / 2
            rrect(ax, x, -0.3, bw, v + 0.3, col, r_px=7)
            ax.text(x + bw / 2, v + 0.12, f"{v:.1f}", ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=col)
    lx = 0.07
    for k, name, col in MODELS:
        fig.patches.append(FancyBboxPatch((lx, 0.783), 0.012, 0.022, boxstyle="round,pad=0,rounding_size=0.004", fc=col, ec="none", transform=fig.transFigure))
        fig.text(lx + 0.02, 0.794, name, fontsize=9.5, va="center", color=TEXT)
        lx += 0.2
    fig.savefig(OUT / "03-category-scores.png", dpi=DPI)
    plt.close(fig)


# ---------- 4. quality vs speed ---------------------------------------------
def chart_tradeoff():
    mem = {"qwen3-4b-instruct": 2.9, "qwen3-8b": 5.7, "cyber-8b": 5.4}
    fig = plt.figure(figsize=(10, 6), dpi=DPI)
    header(fig, "Quality vs speed", "Each bubble is a model · bubble area = memory loaded in Ollama")
    ax = fig.add_axes([0.08, 0.15, 0.88, 0.63])
    ax.set_xlim(0, 75); ax.set_ylim(0, 5)
    ax.axvline(37.5, color=GRID, lw=1, ls=(0, (4, 4))); ax.axhline(2.5, color=GRID, lw=1, ls=(0, (4, 4)))
    ax.set_xlabel("average generation speed (tokens / second)  →  faster", fontsize=9, labelpad=10)
    ax.set_ylabel("average score (0–5)  →  better", fontsize=9, labelpad=10)
    ax.tick_params(length=0, labelsize=9, pad=6)
    for t, (x, y, ha, va) in {"slow · weak": (1.5, 0.1, "left", "bottom"), "fast · weak": (73.5, 0.1, "right", "bottom"),
                              "slow · strong": (1.5, 4.9, "left", "top"), "fast · strong": (73.5, 4.9, "right", "top")}.items():
        ax.text(x, y, t.upper(), fontsize=7.5, color="#4C5886", ha=ha, va=va, fontweight="bold")
    for k, name, col in MODELS:
        xs = speed[speed.model == k].eval_rate_tok_s.mean(); ys = scores[scores.model == k].score_0_5.mean()
        s = mem[k] ** 2 * 85
        for grow, a in ((3.0, 0.07), (2.0, 0.12), (1.4, 0.2)):
            ax.scatter(xs, ys, s=s * grow, color=col, alpha=a, lw=0, zorder=2)
        ax.scatter(xs, ys, s=s, color=col, ec=BG, lw=2, zorder=3)
        txt = f"{name}\n{xs:.1f} tok/s · score {ys:.1f}"
        if k == "qwen3-4b-instruct":
            ax.text(xs, ys + 0.62, txt, ha="center", va="center", fontsize=9.5, color=TEXT, fontweight="bold", linespacing=1.5)
        else:
            ax.text(xs + 9.5, ys, txt, ha="left", va="center", fontsize=9.5, color=TEXT, fontweight="bold", linespacing=1.5)
    fig.savefig(OUT / "04-quality-vs-speed.png", dpi=DPI)
    plt.close(fig)


# ---------- 5. GPU offload ---------------------------------------------------
def chart_offload():
    off = pd.read_csv(RES / "offload.csv")
    fig = plt.figure(figsize=(10, 5.6), dpi=DPI)
    header(fig, "How much of each model runs on the GPU", "Output of `ollama ps` · a 6 GB laptop GPU leaves ~5.7 GB usable for the model")
    ax = fig.add_axes([0.36, 0.1, 0.38, 0.68])
    n = len(off)
    ax.set_xlim(0, 100); ax.set_ylim(n, 0); ax.axis("off")
    labels = {"default env": "default settings", "flash attention + KV cache env vars": "flash attn + q8 KV cache",
              "same + context 2048": "same, context reduced"}
    for i, r in off.iterrows():
        y = i + 0.5
        col = MCOL[r.model]
        fig.text(0.34, 0.78 - (i + 0.5) / n * 0.68 + 0.015, MNAME[r.model], ha="right", fontsize=10.5, fontweight="bold", color=col, va="center")
        fig.text(0.34, 0.78 - (i + 0.5) / n * 0.68 - 0.027, f"{labels.get(r.setting, r.setting)} · ctx {int(r.num_ctx)}", ha="right",
                 fontsize=7.8, color=MUTED, va="center")
        g, c = r.gpu_pct, r.cpu_pct
        rrect(ax, 0, y - 0.2, g - (0.6 if c else 0), 0.4, BLUE, r_px=9)
        ax.text(g / 2, y, f"{int(g)}% GPU", ha="center", va="center", fontsize=9, fontweight="bold", color=BG)
        if c:
            rrect(ax, g + 0.6, y - 0.2, c - 0.6, 0.4, CORAL, r_px=9)
            ax.text(g + c / 2 + 0.3, y, f"{int(c)}%", ha="center", va="center", fontsize=9, fontweight="bold", color=BG)
        fig.text(0.765, 0.78 - (i + 0.5) / n * 0.68, f"{r.loaded_size_gb:.1f} GB", fontsize=11, fontweight="bold", va="center", color=TEXT)
        fig.text(0.84, 0.78 - (i + 0.5) / n * 0.68, f"{r.eval_rate_tok_s:.1f} tok/s", fontsize=9, va="center", color=MUTED)
    for (txt, col), x in zip((("GPU", BLUE), ("CPU (spill-over)", CORAL)), (0.36, 0.43)):
        fig.patches.append(FancyBboxPatch((x, 0.783), 0.012, 0.022, boxstyle="round,pad=0,rounding_size=0.004", fc=col, ec="none", transform=fig.transFigure))
        fig.text(x + 0.02, 0.794, txt, fontsize=9, va="center")
    fig.text(0.765, 0.788, "LOADED", fontsize=7.5, color="#6E7BA8", fontweight="bold")
    fig.text(0.84, 0.788, "SPEED*", fontsize=7.5, color="#6E7BA8", fontweight="bold")
    fig.text(0.955, 0.018, "*single runs on different prompts; Foundation-Sec = mean of 9 runs", fontsize=7.5, color="#5B6794", ha="right", va="bottom")
    fig.savefig(OUT / "05-gpu-offload.png", dpi=DPI)
    plt.close(fig)


# ---------- 6. response time -------------------------------------------------
def chart_time():
    fig = plt.figure(figsize=(10, 7.2), dpi=DPI)
    header(fig, "Time to a complete answer", "Total duration per prompt, log scale · includes any reasoning text the model printed")
    ax = fig.add_axes([0.33, 0.1, 0.62, 0.68])
    ax.set_xscale("log"); ax.set_xlim(1, 420); ax.set_ylim(len(PROMPTS) - 0.4, -0.7)
    ticks = [1, 2, 5, 10, 20, 50, 100]
    ax.set_xticks(ticks); ax.set_xticklabels([f"{t} s" for t in ticks]); ax.minorticks_off()
    ax.set_yticks([]); ax.tick_params(length=0, labelsize=9, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for i, p in enumerate(PROMPTS):
        vals = {}
        for k, _, _ in MODELS:
            r = speed[(speed.prompt == p) & (speed.model == k)].iloc[0]
            vals[k] = r.total_duration_s
        v = [x for x in vals.values() if pd.notna(x)]
        ax.plot([min(v), max(v)], [i, i], color="#2C3764", lw=2.4, solid_capstyle="round", zorder=1)
        for k, _, col in MODELS:
            if pd.notna(vals[k]):
                ax.scatter(vals[k], i, s=110, color=col, ec=BG, lw=1.8, zorder=3)
            else:
                ax.scatter(115, i, s=120, marker="X", color=col, ec=BG, lw=1, zorder=3)
                ax.text(140, i, "loop, no answer", va="center", fontsize=8, color=col, fontweight="bold")
        ax.text(0.82, i, f"{p}  {PLABEL[p]}", ha="right", va="center", fontsize=8.8, color=TEXT)
    lx = 0.33
    for k, name, col in MODELS:
        fig.patches.append(FancyBboxPatch((lx, 0.826), 0.012, 0.022 * 5.4 / 7.2 * 1.35, boxstyle="round,pad=0,rounding_size=0.004", fc=col, ec="none", transform=fig.transFigure))
        fig.text(lx + 0.02, 0.837, name, fontsize=9.5, va="center")
        lx += 0.2
    fig.savefig(OUT / "06-response-time.png", dpi=DPI)
    plt.close(fig)


# ---------- banner -----------------------------------------------------------
def banner():
    W, H = 16, 4.4
    fig = plt.figure(figsize=(W, H), dpi=125)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    gx, gy = np.meshgrid(np.linspace(0, 1, 800), np.linspace(0, 1, 220))
    c0, c1 = np.array([0x0B, 0x10, 0x20]) / 255, np.array([0x1C, 0x14, 0x4D]) / 255
    t = np.clip(gx * 0.85 + (1 - gy) * 0.15, 0, 1)[..., None]
    img = c0 * (1 - t) + c1 * t
    for (cx, cy, rr, col, a) in ((13.2, 3.6, 4.2, np.array([0xC0, 0x84, 0xFC]) / 255, 0.30),
                                 (11.2, 0.4, 3.6, np.array([0x2D, 0xD4, 0xBF]) / 255, 0.22),
                                 (15.2, 0.6, 2.6, np.array([0xFB, 0xBF, 0x24]) / 255, 0.14)):
        d = np.sqrt(((gx * W - cx)) ** 2 + ((gy * H - cy)) ** 2)
        m = np.exp(-(d / rr) ** 2)[..., None] * a
        img = img * (1 - m) + col * m
    ax.imshow(img, extent=[0, W, 0, H], origin="lower", aspect="auto", zorder=0, interpolation="bilinear")
    ax.text(0.55, 3.62, "BENCHMARK  ·  LOCAL LLMS  ·  CYBERSECURITY", fontsize=10.5, color=TEAL, fontweight="bold")
    ax.text(0.55, 2.78, "Local LLMs for Cybersecurity", fontsize=39, fontweight="bold", color="white", va="center")
    ax.text(0.55, 2.0, "Three models, ten prompts, one 6 GB laptop GPU", fontsize=17, color="#C9D1F0", va="center")
    x = 0.55
    for name, col in (("Qwen3 4B Instruct", TEAL), ("Qwen3 8B", AMBER), ("Foundation-Sec 8B", VIOLET)):
        w = 0.42 + 0.145 * len(name)
        ax.add_patch(FancyBboxPatch((x, 0.78), w, 0.5, boxstyle="round,pad=0,rounding_size=0.25", fc="#ffffff10", ec=col, lw=1.4, zorder=3))
        ax.add_patch(Circle((x + 0.3, 1.03), 0.09, fc=col, ec="none", zorder=4))
        ax.text(x + 0.52, 1.03, name, fontsize=12, color="white", va="center", fontweight="medium", zorder=4)
        x += w + 0.25
    sc = scores.groupby("model").score_0_5.mean(); sp = speed.groupby("model").eval_rate_tok_s.mean()
    x0, y0, cw, ch = 10.2, 0.5, 5.25, 3.4
    ax.add_patch(FancyBboxPatch((x0, y0), cw, ch, boxstyle="round,pad=0,rounding_size=0.3", fc="#0B1020", ec="#ffffff30", lw=1, alpha=0.62, zorder=3))
    ax.text(x0 + 0.38, y0 + ch - 0.5, "AVERAGE SCORE  (0–5)", fontsize=9.5, color=MUTED, fontweight="bold", zorder=5, va="center")
    for i, (k, name, col) in enumerate(sorted(MODELS, key=lambda m: -sc[m[0]])):
        yy = y0 + ch - 1.3 - i * 0.92
        ax.text(x0 + 0.38, yy + 0.2, name, fontsize=11, color="white", fontweight="medium", zorder=5, va="center")
        ax.text(x0 + cw - 0.38, yy + 0.2, f"{sp[k]:.0f} tok/s", fontsize=9, color=MUTED, zorder=5, va="center", ha="right")
        tw = cw - 1.5
        ax.add_patch(FancyBboxPatch((x0 + 0.38, yy - 0.2), tw, 0.2, boxstyle="round,pad=0,rounding_size=0.1", fc="#ffffff14", ec="none", zorder=4))
        ax.add_patch(FancyBboxPatch((x0 + 0.38, yy - 0.2), tw * sc[k] / 5, 0.2, boxstyle="round,pad=0,rounding_size=0.1", fc=col, ec="none", zorder=5))
        ax.text(x0 + 0.38 + tw + 0.18, yy - 0.1, f"{sc[k]:.1f}", fontsize=14, color=col, fontweight="bold", zorder=5, va="center")
    ax.text(0.55, 0.32, "Ollama  ·  ASUS Vivobook  ·  RTX 4050 Laptop GPU (6 GB)  ·  scored against ground truth", fontsize=10.5, color=MUTED, va="center")
    fig.savefig(OUT / "banner.png", dpi=125)
    plt.close(fig)


if __name__ == "__main__":
    chart_speed(); chart_heatmap(); chart_categories(); chart_tradeoff(); chart_offload(); chart_time(); banner()
    print("charts written to", OUT)
