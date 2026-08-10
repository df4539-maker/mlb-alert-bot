"""Genera calendario mensual HTML de P&L diario (forward Hondubet).

Salida:
  C:\\Documentos C\\Apuestas deportivas\\calendario_mensual.html

Uso:
  python scripts/plot_calendario_mensual.py
  python scripts/plot_calendario_mensual.py --year 2026 --month 8
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FWD = ROOT / "data" / "forward_bets.csv"
OUT_DIR = Path(r"C:\Documentos C\Apuestas deportivas")
OUT_HTML = OUT_DIR / "calendario_mensual.html"
OUT_JSON = OUT_DIR / "calendario_mensual_data.json"


def _profit_and_payout(row: dict) -> tuple[float, float, float] | None:
    """Return (stake, payout_returned, profit) for settled bets."""
    res = (row.get("result") or "").strip().lower()
    if res not in ("win", "loss"):
        return None
    stake = float(row.get("stake") or 0)
    odds = float(row.get("decimal_odds") or 0)
    notes = row.get("notes") or ""
    if res == "loss":
        return stake, 0.0, -stake
    m = re.search(r"payout=(\d+\.?\d*)", notes)
    payout = float(m.group(1)) if m else stake * odds
    return stake, payout, payout - stake


def load_daily() -> dict[str, dict]:
    """Aggregate settled bets by game_date."""
    days: dict[str, dict] = defaultdict(
        lambda: {"stake": 0.0, "returned": 0.0, "net": 0.0, "n": 0, "w": 0, "l": 0}
    )
    rows = list(csv.DictReader(FWD.open(encoding="utf-8")))
    for r in rows:
        parsed = _profit_and_payout(r)
        if parsed is None:
            continue
        stake, returned, profit = parsed
        d = r.get("game_date") or ""
        if not d:
            continue
        days[d]["stake"] += stake
        days[d]["returned"] += returned
        days[d]["net"] += profit
        days[d]["n"] += 1
        if (r.get("result") or "").lower() == "win":
            days[d]["w"] += 1
        else:
            days[d]["l"] += 1
    # round
    out = {}
    for d, v in days.items():
        stake = v["stake"]
        net = v["net"]
        out[d] = {
            "stake": round(stake, 2),
            "returned": round(v["returned"], 2),
            "net": round(net, 2),
            "roi_pct": round(100 * net / stake, 1) if stake else 0.0,
            "n": v["n"],
            "w": v["w"],
            "l": v["l"],
        }
    return out


def month_grid(year: int, month: int, daily: dict[str, dict]) -> dict:
    cal = calendar.Calendar(firstweekday=0)  # Monday
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(None)
                continue
            key = f"{year:04d}-{month:02d}-{day:02d}"
            info = daily.get(key)
            row.append({"day": day, "date": key, "data": info})
        weeks.append(row)

    # month totals
    prefix = f"{year:04d}-{month:02d}-"
    month_days = {k: v for k, v in daily.items() if k.startswith(prefix)}
    m_stake = sum(v["stake"] for v in month_days.values())
    m_ret = sum(v["returned"] for v in month_days.values())
    m_net = sum(v["net"] for v in month_days.values())
    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "weeks": weeks,
        "totals": {
            "stake": round(m_stake, 2),
            "returned": round(m_ret, 2),
            "net": round(m_net, 2),
            "roi_pct": round(100 * m_net / m_stake, 1) if m_stake else 0.0,
            "days_with_bets": len(month_days),
        },
    }


def render_html(payload: dict) -> str:
    year = payload["year"]
    month = payload["month"]
    name = payload["month_name"]
    totals = payload["totals"]
    updated = payload["updated_at"]
    t_cls = "pos" if totals["net"] > 0 else ("neg" if totals["net"] < 0 else "flat")

    week_rows = []
    for week in payload["weeks"]:
        cells = []
        for cell in week:
            if cell is None:
                cells.append('<td class="empty"></td>')
                continue
            day = cell["day"]
            data = cell["data"]
            if not data:
                cells.append(
                    f'<td class="day idle"><div class="num">{day}</div></td>'
                )
                continue
            cls = "pos" if data["net"] > 0 else ("neg" if data["net"] < 0 else "flat")
            sign = "+" if data["net"] > 0 else ("-" if data["net"] < 0 else "")
            cells.append(
                f"""<td class="day {cls}">
  <div class="num">{day}</div>
  <div class="line"><span>Inv</span> L{data['stake']:.2f}</div>
  <div class="line"><span>Gan</span> L{data['returned']:.2f}</div>
  <div class="net">{sign}L{abs(data['net']):.2f} <small>({sign}{data['roi_pct']:.1f}%)</small></div>
  <div class="wl">{data['w']}W/{data['l']}L</div>
</td>"""
            )
        week_rows.append("<tr>" + "".join(cells) + "</tr>")

    # year nav months that have data
    months_with = sorted({d[:7] for d in payload["daily_keys"]})
    nav = " · ".join(
        f'<a href="?y={ym[:4]}&m={int(ym[5:7])}">{ym}</a>' if False else ym
        for ym in months_with
    )
    # static links won't work without server — list months as text; file is regenerated per month
    months_note = ", ".join(months_with) if months_with else "—"

    t_sign = "+" if totals["net"] > 0 else ("-" if totals["net"] < 0 else "")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Calendario mensual — MLB Forward</title>
<style>
  :root {{
    --bg: #0f1419;
    --card: #1a2332;
    --text: #e7ecf3;
    --muted: #9aa7b8;
    --pos: #1b4332;
    --pos-b: #2d6a4f;
    --neg: #4a1520;
    --neg-b: #9b2226;
    --idle: #15202b;
    --line: #2a3a4f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
    background: #0f1419; color: var(--text); padding: 20px;
  }}
  h1 {{ margin: 0 0 4px; font-size: 1.4rem; }}
  .sub {{ color: var(--muted); margin-bottom: 16px; font-size: 0.9rem; }}
  .summary {{
    display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;
  }}
  .chip {{
    background: var(--card); border: 1px solid var(--line);
    border-radius: 10px; padding: 10px 14px; min-width: 140px;
  }}
  .chip .k {{ color: var(--muted); font-size: 0.75rem; }}
  .chip .v {{ font-size: 1.1rem; font-weight: 700; margin-top: 2px; }}
  .chip.{t_cls} .v {{ color: {"#95d5b2" if totals["net"] > 0 else ("#f4a3a8" if totals["net"] < 0 else "var(--text)")}; }}
  table.cal {{
    width: 100%; border-collapse: separate; border-spacing: 8px;
    table-layout: fixed;
  }}
  th {{
    color: var(--muted); font-weight: 600; font-size: 0.8rem;
    text-align: center; padding: 4px;
  }}
  td.day {{
    vertical-align: top; border-radius: 10px; padding: 8px;
    border: 1px solid var(--line); background: var(--idle);
    height: 110px;
  }}
  td.day.pos {{ background: var(--pos); border-color: var(--pos-b); }}
  td.day.neg {{ background: var(--neg); border-color: var(--neg-b); }}
  td.day.flat {{ background: #243044; }}
  td.day.idle {{ opacity: 0.55; }}
  td.empty {{ background: transparent; border: none; }}
  .num {{ font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; }}
  .line {{ font-size: 0.72rem; color: #d8e0ea; display: flex; justify-content: space-between; gap: 4px; }}
  .line span {{ color: var(--muted); }}
  .net {{ font-weight: 700; font-size: 0.85rem; margin-top: 4px; }}
  .net small {{ font-weight: 600; opacity: 0.9; }}
  .day.pos .net {{ color: #b7f0ce; }}
  .day.neg .net {{ color: #ffc9c9; }}
  .wl {{ font-size: 0.68rem; color: var(--muted); margin-top: 2px; }}
  .legend {{ color: var(--muted); font-size: 0.8rem; margin-top: 12px; }}
  .legend b.pos {{ color: #95d5b2; }}
  .legend b.neg {{ color: #f4a3a8; }}
  footer {{ color: var(--muted); font-size: 0.75rem; margin-top: 16px; }}
  @media (max-width: 800px) {{
    td.day {{ height: auto; font-size: 0.85rem; }}
    .line, .wl {{ font-size: 0.65rem; }}
  }}
</style>
</head>
<body>
  <h1>Calendario mensual — {name} {year}</h1>
  <div class="sub">
    Invertido / Ganado (retorno) / Neto (L y %) · verde = neto + · rojo = neto −<br/>
    Actualizado: {updated} · meses con data: {months_note}
  </div>

  <div class="summary">
    <div class="chip"><div class="k">Días con apuestas</div><div class="v">{totals["days_with_bets"]}</div></div>
    <div class="chip"><div class="k">Invertido mes</div><div class="v">L {totals["stake"]:.2f}</div></div>
    <div class="chip"><div class="k">Ganado (retorno)</div><div class="v">L {totals["returned"]:.2f}</div></div>
    <div class="chip {t_cls}"><div class="k">Neto mes</div><div class="v">{t_sign}L{abs(totals["net"]):.2f} ({t_sign}{totals["roi_pct"]:.1f}%)</div></div>
  </div>

  <table class="cal">
    <thead>
      <tr>
        <th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th><th>Dom</th>
      </tr>
    </thead>
    <tbody>
      {"".join(week_rows)}
    </tbody>
  </table>

  <div class="legend">
    <b class="pos">Verde</b> = día neto positivo &nbsp;·&nbsp;
    <b class="neg">Rojo</b> = día neto negativo &nbsp;·&nbsp;
    Inv = stake &nbsp;·&nbsp; Gan = dinero devuelto (payouts) &nbsp;·&nbsp; Neto = Gan − Inv
  </div>
  <footer>
    Archivo: calendario_mensual.html · regenerar:
    <code>python scripts/plot_calendario_mensual.py --year {year} --month {month}</code>
    · se actualiza al cerrar el día / cuadro baseline.
  </footer>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--month", type=int, default=None)
    args = ap.parse_args()

    daily = load_daily()
    if args.year and args.month:
        year, month = args.year, args.month
    elif daily:
        last = max(daily.keys())
        year, month = int(last[:4]), int(last[5:7])
    else:
        today = date.today()
        year, month = today.year, today.month

    grid = month_grid(year, month, daily)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "daily_keys": sorted(daily.keys()),
        "daily": daily,
        **grid,
    }
    # JSON-serializable weeks (no issues)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    html = render_html(payload)
    OUT_HTML.write_text(html, encoding="utf-8")
    (ROOT / "reports" / "calendario_mensual.html").write_text(html, encoding="utf-8")
    t = payload["totals"]
    print(f"Wrote {OUT_HTML}")
    print(f"{payload['month_name']} {year}: inv={t['stake']:.2f} gan={t['returned']:.2f} neto={t['net']:+.2f} ({t['roi_pct']:+.1f}%)")


if __name__ == "__main__":
    main()
