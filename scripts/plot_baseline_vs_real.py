"""Baseline (backtest) vs Real (forward Hondubet)."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from mlb.betting import bet_payout

ROOT = Path(__file__).resolve().parents[1]
FWD = ROOT / "data" / "forward_bets.csv"
OUT = Path(r"C:\Documentos C\Apuestas deportivas") / "baseline_vs_real.png"

# Baseline backtest (known from live sim)
BASE = {
    "hit": 55.9,
    "roi": 6.7,
    "n": 12041,
    "label": "Baseline backtest\n(-110 simulado)",
}

rows = list(csv.DictReader(FWD.open(encoding="utf-8")))
settled = [r for r in rows if r["result"] in ("win", "loss")]
pending = [r for r in rows if r["result"] == "pending"]

# dedupe pending for display
seen = set()
pending_unique = []
for r in pending:
    k = (r["game_date"], r["away"], r["home"], r["side"], r["stake"], r["decimal_odds"])
    if k in seen:
        continue
    seen.add(k)
    pending_unique.append(r)

staked = 0.0
net = 0.0
wins = 0
lines = []
for r in settled:
    stake = float(r["stake"])
    odds = float(r["decimal_odds"])
    won = r["result"] == "win"
    p = bet_payout(stake, won, odds)
    staked += stake
    net += p
    if won:
        wins += 1
    mark = "W" if won else "L"
    lines.append(f"{mark}  {r['away']}@{r['home']}  {r['side']}  L{stake:g} @{odds:g}  {p:+.2f}")

hit = 100 * wins / len(settled) if settled else 0
roi = 100 * net / staked if staked else 0

plt.style.use("seaborn-v0_8-whitegrid")
fig = plt.figure(figsize=(12, 8), facecolor="#f7f5f1")
fig.suptitle(
    "Baseline vs Real — Forward test Hondubet",
    fontsize=15,
    fontweight="bold",
    color="#1a1a1a",
)
fig.text(
    0.5,
    0.92,
    f"Actualizado con {len(settled)} cerradas · {len(pending_unique)} pending unicas · {len(pending)-len(pending_unique)} duplicados ignorados en conteo",
    ha="center",
    fontsize=9,
    color="#555",
)

gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.2], hspace=0.35, wspace=0.28, left=0.08, right=0.96, top=0.86, bottom=0.08)

# Hit rate compare
ax1 = fig.add_subplot(gs[0, 0])
cats = ["Baseline", "Real"]
vals = [BASE["hit"], hit]
cols = ["#4a6fa5", "#1f6f4a" if hit >= 52.38 else "#8a3b2b"]
bars = ax1.bar(cats, vals, color=cols, width=0.55)
ax1.axhline(52.38, color="#a05a2c", linestyle="--", linewidth=1.2, label="Breakeven -110 (~52.4%)")
ax1.set_ylabel("Win rate (%)")
ax1.set_title("Win rate")
ax1.set_ylim(0, max(70, hit + 10, BASE["hit"] + 10))
ax1.legend(frameon=False, fontsize=8)
for b, v, n in zip(bars, vals, [BASE["n"], len(settled)]):
    ax1.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%\nn={n}", ha="center", fontsize=9)

# ROI compare
ax2 = fig.add_subplot(gs[0, 1])
vals2 = [BASE["roi"], roi]
cols2 = ["#4a6fa5", "#1f6f4a" if roi >= 0 else "#8a3b2b"]
bars2 = ax2.bar(cats, vals2, color=cols2, width=0.55)
ax2.axhline(0, color="#333", linewidth=0.8)
ax2.set_ylabel("ROI (%)")
ax2.set_title("ROI (profit / staked)")
ax2.legend(frameon=False)
for b, v in zip(bars2, vals2):
    ax2.text(b.get_x() + b.get_width() / 2, v + (2 if v >= 0 else -4), f"{v:+.1f}%", ha="center", fontsize=10, fontweight="bold")

# Settled tickets
ax3 = fig.add_subplot(gs[1, 0])
ax3.axis("off")
ax3.set_title("Apuestas cerradas (real)", loc="left", fontsize=11, pad=8)
txt = "\n".join(lines) if lines else "(ninguna)"
txt += f"\n\nStake total: L{staked:g}   Net: {net:+.2f}   ROI: {roi:+.1f}%"
ax3.text(0.02, 0.95, txt, transform=ax3.transAxes, va="top", fontsize=9, family="monospace", color="#222")

# Pending + note
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis("off")
ax4.set_title("Pending / notas", loc="left", fontsize=11, pad=8)
pend_lines = [
    f"· {r['away']}@{r['home']} {r['side']} L{float(r['stake']):g} @{float(r['decimal_odds']):g}"
    for r in pending_unique
] or ["(ninguna)"]
note = (
    "Muestra real aun pequena: no concluye edge.\n"
    "Baseline = historico simulado; Real = Hondubet.\n"
    "Hay duplicados pending (mismo ticket 2 veces):\n"
    "limpia con cuidado antes de cerrar resultados."
)
ax4.text(
    0.02,
    0.95,
    "\n".join(pend_lines[:8]) + ("\n…" if len(pend_lines) > 8 else "") + "\n\n" + note,
    transform=ax4.transAxes,
    va="top",
    fontsize=9,
    color="#222",
)

fig.savefig(OUT, dpi=150)
print(f"OK {OUT}")
print(f"settled={len(settled)} hit={hit:.1f}% roi={roi:+.1f}% net={net:+.2f} pending_u={len(pending_unique)}")
