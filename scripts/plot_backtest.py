"""Grafico descriptivo del backtest live MLB."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "backtest_live.csv"
OUT = Path(r"C:\Documentos C\Apuestas deportivas") / "backtest_analisis.png"

rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
bets = [r for r in rows if (r.get("bet_side") or "").strip()]

by = defaultdict(lambda: {"n": 0, "w": 0, "profit": 0.0, "acc_n": 0, "acc_c": 0})
for r in rows:
    s = str(r["season"])
    by[s]["acc_n"] += 1
    if str(r.get("correct", "")).lower() in ("1", "true", "yes"):
        by[s]["acc_c"] += 1
for r in bets:
    s = str(r["season"])
    by[s]["n"] += 1
    if str(r.get("bet_won", "")).lower() in ("1", "true", "yes"):
        by[s]["w"] += 1
    by[s]["profit"] += float(r.get("profit") or 0)

seasons = sorted(by.keys())
roi = [100 * by[s]["profit"] / by[s]["n"] if by[s]["n"] else 0 for s in seasons]
win = [100 * by[s]["w"] / by[s]["n"] if by[s]["n"] else 0 for s in seasons]
acc = [100 * by[s]["acc_c"] / by[s]["acc_n"] if by[s]["acc_n"] else 0 for s in seasons]
profit = [by[s]["profit"] for s in seasons]
n_bets = [by[s]["n"] for s in seasons]

# Equity curve (todas las apuestas en orden)
equity = [0.0]
for r in bets:
    equity.append(equity[-1] + float(r.get("profit") or 0))

total_bets = len(bets)
total_profit = equity[-1]
total_roi = 100 * total_profit / total_bets if total_bets else 0
wins = sum(1 for r in bets if str(r.get("bet_won", "")).lower() in ("1", "true", "yes"))
hit = 100 * wins / total_bets if total_bets else 0

# Max drawdown
peak = equity[0]
max_dd = 0.0
for v in equity:
    peak = max(peak, v)
    max_dd = max(max_dd, peak - v)

plt.style.use("seaborn-v0_8-whitegrid")
fig = plt.figure(figsize=(14, 10), facecolor="#f7f5f1")
fig.suptitle(
    "Backtest MLB Alert Bot — analisis descriptivo",
    fontsize=16,
    fontweight="bold",
    color="#1a1a1a",
    y=0.98,
)
fig.text(
    0.5,
    0.935,
    "Modo live cronologico · Elo + value bet (edge >= 3%) · cuotas simuladas -110 · 2019–2026",
    ha="center",
    fontsize=10,
    color="#555555",
)

gs = fig.add_gridspec(3, 2, height_ratios=[1.05, 1.15, 1.1], hspace=0.38, wspace=0.28, left=0.07, right=0.97, top=0.90, bottom=0.07)

# KPI strip as text boxes in first row spanning
ax0 = fig.add_subplot(gs[0, :])
ax0.axis("off")
kpis = [
    ("Partidos", f"{len(rows):,}".replace(",", ".")),
    ("Apuestas value", f"{total_bets:,}".replace(",", ".")),
    ("Win rate", f"{hit:.1f}%"),
    ("ROI total", f"{total_roi:+.1f}%"),
    ("Profit", f"{total_profit:+.0f} u"),
    ("Max drawdown", f"{max_dd:.0f} u"),
]
colors = ["#2c3e50", "#2c3e50", "#1f6f4a" if hit >= 52.4 else "#8a3b2b", "#1f6f4a" if total_roi > 0 else "#8a3b2b", "#1f6f4a" if total_profit > 0 else "#8a3b2b", "#8a5a00"]
for i, ((lab, val), c) in enumerate(zip(kpis, colors)):
    x = 0.02 + i * 0.165
    ax0.add_patch(plt.Rectangle((x, 0.15), 0.15, 0.7, transform=ax0.transAxes, facecolor="#ffffff", edgecolor="#d0cbc3", linewidth=1))
    ax0.text(x + 0.075, 0.62, val, transform=ax0.transAxes, ha="center", va="center", fontsize=15, fontweight="bold", color=c)
    ax0.text(x + 0.075, 0.32, lab, transform=ax0.transAxes, ha="center", va="center", fontsize=9, color="#666666")

# ROI bars
ax1 = fig.add_subplot(gs[1, 0])
bar_colors = ["#1f6f4a" if v >= 0 else "#8a3b2b" for v in roi]
ax1.bar(seasons, roi, color=bar_colors, width=0.65, edgecolor="none")
ax1.axhline(0, color="#333", linewidth=0.8)
ax1.axhline(total_roi, color="#4a6fa5", linestyle="--", linewidth=1.2, label=f"ROI total {total_roi:+.1f}%")
ax1.set_title("ROI por temporada (apuestas value)", fontsize=12, pad=8)
ax1.set_ylabel("ROI (%)")
ax1.set_xlabel("Temporada")
ax1.legend(frameon=False, fontsize=9)
ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0f%%"))

# Accuracy vs baseline
ax2 = fig.add_subplot(gs[1, 1])
ax2.plot(seasons, acc, marker="o", color="#2c3e50", linewidth=2, label="Accuracy modelo")
ax2.axhline(53.1, color="#a05a2c", linestyle="--", linewidth=1.2, label="Baseline siempre local 53.1%")
ax2.set_ylim(50, 58)
ax2.set_title("Accuracy del modelo vs baseline", fontsize=12, pad=8)
ax2.set_ylabel("Accuracy (%)")
ax2.set_xlabel("Temporada")
ax2.legend(frameon=False, fontsize=9)

# Equity curve
ax3 = fig.add_subplot(gs[2, 0])
ax3.plot(range(len(equity)), equity, color="#1f6f4a", linewidth=1.2)
ax3.fill_between(range(len(equity)), equity, 0, where=[v >= 0 for v in equity], color="#1f6f4a", alpha=0.15)
ax3.fill_between(range(len(equity)), equity, 0, where=[v < 0 for v in equity], color="#8a3b2b", alpha=0.2)
ax3.set_title("Curva de bankroll (profit acumulado)", fontsize=12, pad=8)
ax3.set_xlabel("Nº de apuesta (orden cronologico)")
ax3.set_ylabel("Unidades (u)")

# Win rate + volumen
ax4 = fig.add_subplot(gs[2, 1])
ax4b = ax4.twinx()
ax4.bar(seasons, n_bets, color="#c8d4e0", width=0.65, label="# apuestas")
ax4b.plot(seasons, win, marker="s", color="#2c3e50", linewidth=2, label="Win rate %")
ax4b.axhline(52.38, color="#a05a2c", linestyle="--", linewidth=1, label="Breakeven ~52.4% (-110)")
ax4.set_title("Volumen y win rate por temporada", fontsize=12, pad=8)
ax4.set_ylabel("Apuestas")
ax4b.set_ylabel("Win rate (%)")
ax4.set_xlabel("Temporada")
lines1, lab1 = ax4.get_legend_handles_labels()
lines2, lab2 = ax4b.get_legend_handles_labels()
ax4.legend(lines1 + lines2, lab1 + lab2, frameon=False, fontsize=8, loc="upper right")

fig.text(
    0.5,
    0.015,
    "Nota: cuotas simuladas -110 (no Hondubet). El ROI real en forward test suele ser menor. 2026 = temporada en curso.",
    ha="center",
    fontsize=8,
    color="#777777",
)

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=160)
print(f"OK {OUT}")
print(f"ROI={total_roi:.1f}% profit={total_profit:.1f} dd={max_dd:.1f} hit={hit:.1f}%")
