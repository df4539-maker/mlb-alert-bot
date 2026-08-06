"""Refresh FORWARD_STATUS.md with official filter + today's card; then commit via shell."""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlb.api import MLBApiClient
from mlb.betting import DEFAULT_DECIMAL_ODDS, bet_payout, decimal_to_implied_prob
from mlb.database import fetch_final_games, get_connection, init_db
from mlb.elo import EloModel
from mlb.predict import train_model_from_history

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    init_db()
    abbr: dict[str, int] = {}
    with get_connection() as conn:
        for row in conn.execute("SELECT team_id, abbreviation FROM teams"):
            abbr[row["abbreviation"].upper()] = int(row["team_id"])
        games = list(fetch_final_games(conn))
    for a, b in [("TB", "TBR"), ("CWS", "CHW"), ("KC", "KCR"), ("ATH", "OAK")]:
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

    rows = [
        r
        for r in csv.DictReader((ROOT / "data" / "forward_bets.csv").open(encoding="utf-8"))
        if r["result"] in ("win", "loss")
    ]
    rows.sort(key=lambda r: (r["game_date"], r["logged_at"]))
    official = []
    for r in rows:
        a, h, side = r["away"], r["home"], r["side"]
        m = elo_asof(r["game_date"])
        aid = tid(a, "TBR" if a == "TB" else a, "OAK" if a == "ATH" else a)
        hid = tid(h, "TBR" if h == "TB" else h, "OAK" if h == "ATH" else h)
        pred = m.predict(hid, aid)
        p = pred.home_win_prob if side == "home" else pred.away_win_prob
        odds = float(r["decimal_odds"])
        stake = float(r["stake"])
        edge = p - (1 / odds)
        if p < 0.5 or edge < 0.03:
            continue
        won = r["result"] == "win"
        profit = bet_payout(stake, won, odds)
        lado = f"{h}(1)" if side == "home" else f"{a}(2)"
        official.append((r["game_date"], a, h, lado, odds, stake, p, edge, won, profit))

    model, teams = train_model_from_history()
    abbr_map = {tid_: v["abbr"].upper() for tid_, v in teams.items()}
    client = MLBApiClient()
    now = datetime.now(timezone.utc)
    market = decimal_to_implied_prob(DEFAULT_DECIMAL_ODDS)
    start = datetime(2026, 8, 6, 6, 0, tzinfo=timezone.utc)
    end = datetime(2026, 8, 7, 6, 0, tzinfo=timezone.utc)
    today = []
    for g in client.fetch_season_schedule(2026):
        st = g.get("status", {})
        if st.get("abstractGameState") != "Preview":
            continue
        det = (st.get("detailedState") or "").lower()
        if "warmup" in det or "in progress" in det:
            continue
        gd = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
        if gd < start or gd >= end or gd <= now + timedelta(minutes=15):
            continue
        away = g["teams"]["away"]["team"]
        home = g["teams"]["home"]["team"]
        pred = model.predict(home["id"], away["id"])
        a = (away.get("abbreviation") or abbr_map.get(away["id"], "?")).upper()
        h = (home.get("abbreviation") or abbr_map.get(home["id"], "?")).upper()
        for old, new in [("TBR", "TB"), ("CHW", "CWS"), ("KCR", "KC"), ("OAK", "ATH")]:
            if a == old:
                a = new
            if h == old:
                h = new
        he = pred.home_win_prob - market
        ae = pred.away_win_prob - market
        if he >= ae:
            p, edge, pick, num = pred.home_win_prob, he, h, "1"
        else:
            p, edge, pick, num = pred.away_win_prob, ae, a, "2"
        if p >= 0.5 and edge >= 0.03:
            stake = 20 if edge >= 0.09 else 15
            today.append((a, h, pick, num, p, 1 / p, edge, stake))
    today.sort(key=lambda x: -x[6])

    lines = [
        "# Forward test — estado",
        "",
        "## Filtro oficial (FIJO)",
        "",
        "- Solo cuenta / solo apostar: **P modelo >= 50% (CON)** y **edge >= +3%** vs cuota real.",
        "- CONTRA o CON sin value: fuera de protocolo.",
        "- Meta **250** ops oficiales.",
        "",
        "## Oficiales cerradas (CON + edge>=3%)",
        "",
        "| # | Fecha | Partido | Lado | Cuota | Stake | P | Edge | Resultado | Profit |",
        "|---|-------|---------|------|-------|-------|---|------|-----------|--------|",
    ]
    net = staked = 0.0
    wins = 0
    for i, (d, a, h, lado, odds, stake, p, edge, won, profit) in enumerate(official, 1):
        res = "GANÓ" if won else "PERDIÓ"
        lines.append(
            f"| {i} | {d} | {a} @ {h} | {lado} | {odds:.2f} | L{stake:g} | "
            f"{p*100:.1f}% | {edge*100:+.1f}% | {res} | {profit:+.2f} |"
        )
        net += profit
        staked += stake
        wins += int(won)
    n = len(official)
    lines += [
        "",
        f"**Oficial:** {wins}W / {n-wins}L · stake L{staked:g} · neto **{net:+.2f}** · "
        f"ROI **{100*net/staked:+.1f}%** · contador **{n} / 250**",
        "",
        "Baseline: win 55.9% · ROI +6.7%.",
        "",
        "## Card 2026-08-06",
        "",
        "| # | Partido | Apostá | Lado | P | Cuota modelo | Edge | Stake sug. |",
        "|---|---------|--------|------|---|--------------|------|------------|",
    ]
    for i, (a, h, pick, num, p, cm, edge, stake) in enumerate(today, 1):
        lines.append(
            f"| {i} | {a} @ {h} | **{pick}** | **{num}** | {p*100:.1f}% | {cm:.2f} | "
            f"{edge*100:+.1f}% | L{stake} |"
        )
    lines += [
        "",
        "Verificar cuota Hondubet: si edge real < 3%, saltar. Prioridad bank chico: 1-5.",
        "",
        "CSV: `data/forward_bets.csv` · Rutina: `reports/RUTINA.md`",
        "",
    ]
    (ROOT / "reports" / "FORWARD_STATUS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"OK official={n} W={wins} net={net:+.2f} today={len(today)}")


if __name__ == "__main__":
    main()
