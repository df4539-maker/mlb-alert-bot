"""Complete Elo as-of edge for closed forward bets; clean CSV; update report."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from mlb.betting import bet_payout
from mlb.database import fetch_final_games, get_connection, init_db
from mlb.elo import EloModel
from mlb.forward_log import FIELDNAMES, FORWARD_CSV

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    init_db()
    abbr: dict[str, int] = {}
    with get_connection() as conn:
        for row in conn.execute("SELECT team_id, abbreviation FROM teams"):
            abbr[row["abbreviation"].upper()] = int(row["team_id"])
        games = list(fetch_final_games(conn))

    for a, b in [
        ("TB", "TBR"),
        ("CWS", "CHW"),
        ("KC", "KCR"),
        ("ATH", "OAK"),
        ("WSH", "WAS"),
    ]:
        if a in abbr and b not in abbr:
            abbr[b] = abbr[a]
        if b in abbr and a not in abbr:
            abbr[a] = abbr[b]

    def tid(*names: str) -> int:
        for n in names:
            if n.upper() in abbr:
                return abbr[n.upper()]
        raise KeyError(names)

    def elo_asof(game_date: str) -> EloModel:
        m = EloModel()
        for g in games:
            gd = str(g["game_date"])[:10]
            if gd >= game_date:
                continue
            if g["home_win"] is None:
                continue
            m.update(int(g["home_team_id"]), int(g["away_team_id"]), int(g["home_win"]))
        return m

    def predict_side(m: EloModel, away: str, home: str, side: str) -> float:
        aid = tid(away, "TBR" if away == "TB" else away, "OAK" if away == "ATH" else away)
        hid = tid(home, "TBR" if home == "TB" else home, "OAK" if home == "ATH" else home)
        pred = m.predict(hid, aid)
        return pred.home_win_prob if side == "home" else pred.away_win_prob

    closed = [
        dict(game_date="2026-08-02", away="BOS", home="LAD", side="away", stake=25, odds=2.55, result="win", notes="ticket=5256503135; #1"),
        dict(game_date="2026-08-03", away="TB", home="COL", side="home", stake=10, odds=1.55, result="win", notes="ticket=5259564754; #2"),
        dict(game_date="2026-08-03", away="PIT", home="MIL", side="home", stake=10, odds=1.64, result="loss", notes="ticket=5259490664; #3"),
        dict(game_date="2026-08-03", away="LAD", home="CHC", side="away", stake=10, odds=1.80, result="loss", notes="ticket=5259506896; #4"),
        dict(game_date="2026-08-03", away="STL", home="NYY", side="home", stake=10, odds=1.45, result="loss", notes="viaje#5; NYY home"),
        dict(game_date="2026-08-04", away="ATH", home="CIN", side="away", stake=20, odds=2.15, result="loss", notes="viaje#6; ATH away"),
        dict(game_date="2026-08-04", away="LAA", home="BAL", side="home", stake=10, odds=1.76, result="win", notes="viaje#7; BAL home"),
        dict(game_date="2026-08-04", away="TOR", home="HOU", side="home", stake=10, odds=1.80, result="win", notes="viaje#8; HOU home"),
    ]

    results = []
    print("n|fecha|partido|lado|cuota|P|cuota_mod|edge|con_contra|res|profit")
    for i, b in enumerate(closed, 1):
        m = elo_asof(b["game_date"])
        p = predict_side(m, b["away"], b["home"], b["side"])
        implied = 1 / b["odds"]
        edge = p - implied
        cuota_mod = 1 / p
        con = "con" if p >= 0.5 else "contra"
        won = b["result"] == "win"
        profit = bet_payout(b["stake"], won, b["odds"])
        lado = f"{b['home']}(1)" if b["side"] == "home" else f"{b['away']}(2)"
        print(
            f"{i}|{b['game_date']}|{b['away']}@{b['home']}|{lado}|{b['odds']:.2f}|"
            f"{p*100:.1f}%|{cuota_mod:.2f}|{edge*100:+.1f}%|{con}|{b['result']}|{profit:+.2f}"
        )
        results.append(
            {
                **b,
                "p": p,
                "cuota_mod": cuota_mod,
                "edge": edge,
                "con": con,
                "profit": profit,
                "lado": lado,
            }
        )

    old = list(csv.DictReader(FORWARD_CSV.open(encoding="utf-8")))
    keep_pending = []
    seen_t: set[str] = set()
    for r in old:
        note = r.get("notes") or ""
        if r.get("result") != "pending":
            continue
        if "ticket=" not in note:
            continue
        if r.get("game_date") != "2026-08-05":
            continue
        tid = note.split("ticket=")[1].split(";")[0]
        if tid in seen_t:
            continue
        seen_t.add(tid)
        keep_pending.append(r)

    now = datetime.now(timezone.utc).isoformat()
    out_rows = []
    for b in results:
        out_rows.append(
            {
                "logged_at": now,
                "game_date": b["game_date"],
                "away": b["away"],
                "home": b["home"],
                "side": b["side"],
                "stake": f"{b['stake']:.2f}",
                "decimal_odds": f"{b['odds']:.3f}",
                "american_odds": "",
                "result": b["result"],
                "notes": f"{b['notes']}; P={b['p']*100:.1f}%; edge={b['edge']*100:+.1f}%; {b['con']}",
            }
        )
    out_rows.extend(keep_pending)

    FORWARD_CSV.parent.mkdir(parents=True, exist_ok=True)
    with FORWARD_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(out_rows)
    print("CSV_ROWS", len(out_rows), "pending", len(keep_pending))

    lines = [
        "# Forward test — estado",
        "",
        "## Cerradas (P modelo **as-of** fecha del partido)",
        "",
        "| # | Fecha | Partido | Lado | Cuota | Stake | P modelo | Cuota modelo | Edge | Con/Contra | Resultado | Profit |",
        "|---|-------|---------|------|-------|-------|----------|--------------|------|------------|-----------|--------|",
    ]
    net = staked = wins = 0.0
    wins_i = 0
    for i, b in enumerate(results, 1):
        res = "GANÓ" if b["result"] == "win" else "PERDIÓ"
        lines.append(
            f"| {i} | {b['game_date']} | {b['away']} @ {b['home']} | {b['lado']} | "
            f"{b['odds']:.2f} | L{b['stake']:g} | {b['p']*100:.1f}% | {b['cuota_mod']:.2f} | "
            f"{b['edge']*100:+.1f}% | {b['con']} | {res} | {b['profit']:+.2f} |"
        )
        net += b["profit"]
        staked += b["stake"]
        wins_i += int(b["result"] == "win")
    lines += [
        "",
        f"**Resumen cerradas:** {wins_i}W / {len(results)-wins_i}L · stake L{staked:g} · "
        f"neto **{net:+.2f}** · hit {100*wins_i/len(results):.0f}%",
        "",
        "Baseline backtest: win 55.9% · ROI +6.7% (cuotas simuladas -110).",
        "",
        "Elo as-of: entrenado solo con partidos **anteriores** a `game_date` (sin leak del propio juego).",
        "",
        "## Pendientes 2026-08-05 (tickets reales; basura BOS Telegram eliminada)",
        "",
        "| Partido | Lado | Cuota | Stake | Ticket |",
        "|---------|------|-------|-------|--------|",
    ]
    for r in keep_pending:
        side = r["side"]
        a, h = r["away"], r["home"]
        lado = f"{h} (1)" if side == "home" else f"{a} (2)"
        note = r.get("notes") or ""
        tid = note.split("ticket=")[1].split(";")[0] if "ticket=" in note else ""
        lines.append(
            f"| {a} @ {h} | {lado} | {r['decimal_odds']} | L{float(r['stake']):g} | {tid} |"
        )
    lines += [
        "",
        f"Pendientes: **{len(keep_pending)}** · Fuente: `data/forward_bets.csv`",
        "",
        "Gráficos: `reports/backtest_analisis.png`, `reports/baseline_vs_real.png`",
        "",
    ]
    (ROOT / "reports" / "FORWARD_STATUS.md").write_text("\n".join(lines), encoding="utf-8")
    print("WROTE reports/FORWARD_STATUS.md")


if __name__ == "__main__":
    main()
