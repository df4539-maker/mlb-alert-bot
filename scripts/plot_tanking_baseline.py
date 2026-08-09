"""Genera HTML de tanking/equity: Todas | Solo CON | CON+edge>=3% (oficial).

Salida fija (carpeta Apuestas deportivas):
  C:\\Documentos C\\Apuestas deportivas\\tanking_baseline.html

Uso:
  python scripts/plot_tanking_baseline.py
  python scripts/plot_tanking_baseline.py --bank 1543
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FWD = ROOT / "data" / "forward_bets.csv"
BANK_CSV = ROOT / "data" / "bank_snapshots.csv"
OUT_DIR = Path(r"C:\Documentos C\Apuestas deportivas")
OUT_HTML = OUT_DIR / "tanking_baseline.html"
OUT_JSON = OUT_DIR / "tanking_baseline_data.json"
BASE_HIT = 55.9
BASE_ROI = 6.7


def _profit(row: dict) -> float | None:
    res = (row.get("result") or "").strip().lower()
    if res not in ("win", "loss"):
        return None
    stake = float(row.get("stake") or 0)
    odds = float(row.get("decimal_odds") or 0)
    notes = row.get("notes") or ""
    if res == "loss":
        return -stake
    m = re.search(r"payout=(\d+\.?\d*)", notes)
    if m:
        return float(m.group(1)) - stake
    return stake * (odds - 1)


def _edge_p(row: dict) -> tuple[float | None, float | None, bool]:
    notes = row.get("notes") or ""
    em = re.search(r"edge[=~]([+\-]?\d+\.?\d*)%", notes)
    pm = re.search(r"P[=~](\d+\.?\d*)%", notes)
    edge = float(em.group(1)) / 100 if em else None
    p = float(pm.group(1)) / 100 if pm else None
    contra = "contra" in notes.lower()
    return edge, p, contra


def parse_bets() -> list[dict]:
    rows = list(csv.DictReader(FWD.open(encoding="utf-8")))
    out = []
    for r in rows:
        profit = _profit(r)
        if profit is None:
            continue
        edge, p, contra = _edge_p(r)
        out.append(
            {
                "date": r.get("game_date") or "",
                "game": f"{r.get('away')}@{r.get('home')}",
                "side": r.get("side") or "",
                "stake": float(r.get("stake") or 0),
                "odds": float(r.get("decimal_odds") or 0),
                "result": (r.get("result") or "").lower(),
                "profit": profit,
                "edge": edge,
                "p": p,
                "contra": contra,
                "logged_at": r.get("logged_at") or "",
            }
        )
    out.sort(key=lambda b: (b["date"], b["logged_at"]))
    return out


def equity_curve(bets: list[dict]) -> dict:
    labels: list[str] = []
    eq = 0.0
    series: list[float] = []
    details: list[dict] = []
    for i, b in enumerate(bets, 1):
        eq += b["profit"]
        label = f"{i}. {b['date']} {b['game']}"
        labels.append(label)
        series.append(round(eq, 2))
        details.append(
            {
                "n": i,
                "date": b["date"],
                "game": b["game"],
                "result": b["result"],
                "profit": round(b["profit"], 2),
                "equity": round(eq, 2),
                "edge": None if b["edge"] is None else round(b["edge"] * 100, 1),
            }
        )
    wins = sum(1 for b in bets if b["result"] == "win")
    stake = sum(b["stake"] for b in bets)
    net = sum(b["profit"] for b in bets)
    n = len(bets)
    return {
        "n": n,
        "wins": wins,
        "losses": n - wins,
        "hit": round(100 * wins / n, 1) if n else 0.0,
        "roi": round(100 * net / stake, 1) if stake else 0.0,
        "net": round(net, 2),
        "stake": round(stake, 2),
        "labels": labels,
        "equity": series,
        "details": details,
    }


def record_bank(bank: float) -> None:
    BANK_CSV.parent.mkdir(parents=True, exist_ok=True)
    exists = BANK_CSV.exists()
    with BANK_CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["logged_at", "bank"])
        if not exists:
            w.writeheader()
        w.writerow(
            {
                "logged_at": datetime.now(timezone.utc).isoformat(),
                "bank": f"{bank:.2f}",
            }
        )


def load_banks() -> list[dict]:
    if not BANK_CSV.exists():
        return []
    return list(csv.DictReader(BANK_CSV.open(encoding="utf-8")))


def build_payload(bank: float | None) -> dict:
    bets = parse_bets()
    todas = bets
    con = [b for b in bets if not b["contra"] and (b["p"] is None or b["p"] >= 0.50)]
    oficial = [b for b in con if b["edge"] is not None and b["edge"] >= 0.03]
    pref = [b for b in con if b["edge"] is not None and b["edge"] >= 0.10]

    curves = {
        "todas": equity_curve(todas),
        "con": equity_curve(con),
        "oficial": equity_curve(oficial),
        "pref10": equity_curve(pref),
    }

    # Align labels to longest series for multi-line chart: use step index
    max_n = max(curves[k]["n"] for k in curves) or 1
    step_labels = [str(i) for i in range(0, max_n + 1)]

    def padded(curve: dict) -> list[float | None]:
        # start at 0, then equity after each bet of that bucket
        vals: list[float | None] = [0.0]
        vals.extend(curve["equity"])
        while len(vals) < len(step_labels):
            vals.append(None)
        return vals

    if bank is not None:
        record_bank(bank)
    banks = load_banks()

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": {"hit": BASE_HIT, "roi": BASE_ROI},
        "bank": bank,
        "bank_history": banks,
        "risk_l25_pct": round(100 * 25 / bank, 2) if bank else None,
        "curves": curves,
        "chart": {
            "labels": step_labels,
            "todas": padded(curves["todas"]),
            "con": padded(curves["con"]),
            "oficial": padded(curves["oficial"]),
            "pref10": padded(curves["pref10"]),
        },
        "oficial_counter": f"{curves['oficial']['n']}/250",
    }


def render_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    c = data["curves"]
    bank_line = (
        f"Bank Hondubet: <b>L {data['bank']:.2f}</b> · L25 = <b>{data['risk_l25_pct']}%</b> riesgo"
        if data.get("bank") is not None
        else "Bank: (pasa saldo para actualizar riesgo)"
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Tanking Baseline — MLB Forward</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f1419;
    --card: #1a2332;
    --text: #e7ecf3;
    --muted: #9aa7b8;
    --todas: #6ea8fe;
    --con: #63e6be;
    --oficial: #ffd43b;
    --pref: #ffa94d;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
    background: linear-gradient(160deg, #0f1419, #162033 50%, #101820);
    color: var(--text); min-height: 100vh; padding: 24px;
  }}
  h1 {{ margin: 0 0 6px; font-size: 1.5rem; }}
  .sub {{ color: var(--muted); margin-bottom: 18px; font-size: 0.95rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px; }}
  .stat {{
    background: var(--card); border: 1px solid #2a3a4f; border-radius: 12px;
    padding: 14px 16px;
  }}
  .stat .label {{ color: var(--muted); font-size: 0.8rem; }}
  .stat .value {{ font-size: 1.25rem; font-weight: 700; margin-top: 4px; }}
  .stat .meta {{ color: var(--muted); font-size: 0.8rem; margin-top: 4px; }}
  .panel {{
    background: var(--card); border: 1px solid #2a3a4f; border-radius: 14px;
    padding: 16px 18px; margin-bottom: 16px;
  }}
  canvas {{ max-height: 420px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th, td {{ padding: 8px 10px; border-bottom: 1px solid #2a3a4f; text-align: left; }}
  th {{ color: var(--muted); font-weight: 600; }}
  .w {{ color: #63e6be; }}
  .l {{ color: #ff8787; }}
  footer {{ color: var(--muted); font-size: 0.8rem; margin-top: 8px; }}
</style>
</head>
<body>
  <h1>Tanking / Equity — cuadro baseline</h1>
  <div class="sub">
    Actualizado: {data["updated_at"]} · Contador oficial <b>{data["oficial_counter"]}</b><br/>
    {bank_line}<br/>
    Baseline backtest ref: hit {data["baseline"]["hit"]}% · ROI +{data["baseline"]["roi"]}%
  </div>

  <div class="grid">
    <div class="stat">
      <div class="label">Todas</div>
      <div class="value">{c["todas"]["n"]} · {c["todas"]["wins"]}W/{c["todas"]["losses"]}L</div>
      <div class="meta">hit {c["todas"]["hit"]}% · ROI {c["todas"]["roi"]:+.1f}% · neto {c["todas"]["net"]:+.2f}</div>
    </div>
    <div class="stat">
      <div class="label">Solo CON</div>
      <div class="value">{c["con"]["n"]} · {c["con"]["wins"]}W/{c["con"]["losses"]}L</div>
      <div class="meta">hit {c["con"]["hit"]}% · ROI {c["con"]["roi"]:+.1f}% · neto {c["con"]["net"]:+.2f}</div>
    </div>
    <div class="stat">
      <div class="label">CON + edge ≥3% (oficial)</div>
      <div class="value">{c["oficial"]["n"]} · {c["oficial"]["wins"]}W/{c["oficial"]["losses"]}L</div>
      <div class="meta">hit {c["oficial"]["hit"]}% · ROI {c["oficial"]["roi"]:+.1f}% · neto {c["oficial"]["net"]:+.2f}</div>
    </div>
    <div class="stat">
      <div class="label">Preferida ≥10%</div>
      <div class="value">{c["pref10"]["n"]} · {c["pref10"]["wins"]}W/{c["pref10"]["losses"]}L</div>
      <div class="meta">hit {c["pref10"]["hit"]}% · ROI {c["pref10"]["roi"]:+.1f}% · neto {c["pref10"]["net"]:+.2f}</div>
    </div>
  </div>

  <div class="panel">
    <canvas id="eqChart"></canvas>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Detalle oficial (CON + edge ≥3%)</h3>
    <table>
      <thead>
        <tr><th>#</th><th>Fecha</th><th>Partido</th><th>Edge</th><th>Res</th><th>Profit</th><th>Equity</th></tr>
      </thead>
      <tbody>
        {"".join(
            f"<tr><td>{d['n']}</td><td>{d['date']}</td><td>{d['game']}</td>"
            f"<td>{'' if d['edge'] is None else f'{d['edge']:+.1f}%'}</td>"
            f"<td class='{'w' if d['result']=='win' else 'l'}'>{d['result'].upper()}</td>"
            f"<td>{d['profit']:+.2f}</td><td>{d['equity']:+.2f}</td></tr>"
            for d in c["oficial"]["details"]
        )}
      </tbody>
    </table>
  </div>

  <footer>
    Archivo: tanking_baseline.html · regenerar con
    <code>python scripts/plot_tanking_baseline.py --bank SALDO</code>
    · cuando pidas “grafico baseline” se actualiza.
  </footer>

<script>
const DATA = {payload};
const ctx = document.getElementById('eqChart');
new Chart(ctx, {{
  type: 'line',
  data: {{
    labels: DATA.chart.labels,
    datasets: [
      {{
        label: 'Todas',
        data: DATA.chart.todas,
        borderColor: '#6ea8fe',
        backgroundColor: 'rgba(110,168,254,0.12)',
        tension: 0.2,
        spanGaps: false,
        pointRadius: 2,
      }},
      {{
        label: 'Solo CON',
        data: DATA.chart.con,
        borderColor: '#63e6be',
        backgroundColor: 'rgba(99,230,190,0.10)',
        tension: 0.2,
        spanGaps: false,
        pointRadius: 2,
      }},
      {{
        label: 'CON+edge≥3% (oficial)',
        data: DATA.chart.oficial,
        borderColor: '#ffd43b',
        backgroundColor: 'rgba(255,212,59,0.12)',
        tension: 0.2,
        spanGaps: false,
        pointRadius: 3,
        borderWidth: 3,
      }},
      {{
        label: 'Preferida ≥10%',
        data: DATA.chart.pref10,
        borderColor: '#ffa94d',
        borderDash: [6,4],
        tension: 0.2,
        spanGaps: false,
        pointRadius: 2,
      }},
    ]
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      title: {{
        display: true,
        text: 'Equity acumulada (profit) por bucket — tanking',
        color: '#e7ecf3',
        font: {{ size: 14 }}
      }},
      legend: {{ labels: {{ color: '#c5d0de' }} }},
      tooltip: {{
        callbacks: {{
          label: (ctx) => `${{ctx.dataset.label}}: L ${{ctx.parsed.y}}`
        }}
      }}
    }},
    scales: {{
      x: {{
        title: {{ display: true, text: 'Ops en ese bucket (0 = inicio)', color: '#9aa7b8' }},
        ticks: {{ color: '#9aa7b8', maxTicksLimit: 16 }},
        grid: {{ color: 'rgba(255,255,255,0.06)' }}
      }},
      y: {{
        title: {{ display: true, text: 'Equity (Lempiras)', color: '#9aa7b8' }},
        ticks: {{ color: '#9aa7b8' }},
        grid: {{ color: 'rgba(255,255,255,0.06)' }}
      }}
    }}
  }}
}});
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=float, default=None, help="Saldo Hondubet actual")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_payload(args.bank)
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_HTML.write_text(render_html(data), encoding="utf-8")
    # mirror inside repo reports too
    (ROOT / "reports" / "tanking_baseline.html").write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_JSON}")
    print(f"Oficial {data['oficial_counter']} net={data['curves']['oficial']['net']:+.2f}")
    if args.bank is not None:
        print(f"Bank L{args.bank:.2f} · L25 risk {data['risk_l25_pct']}%")


if __name__ == "__main__":
    main()
