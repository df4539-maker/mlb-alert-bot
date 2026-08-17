"""Exporta predicciones Elo PRE-MATCH del día para la PC de viaje.

Salida: data/predictions_YYYY-MM-DD.csv
Columnas: date,away,home,side_con,P,cuota_modelo,hora_HN,game_pk

Uso:
  python scripts/export_daily_predictions.py
  python scripts/export_daily_predictions.py --date 2026-08-17
  python scripts/export_daily_predictions.py --date 2026-08-17 --include-started

La PC de bots genera esto cada mañana → git push.
La PC de viaje hace git pull y arma el card (CON / 3-5-10% / exposición).
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from mlb.api import MLBApiClient
from mlb.predict import train_model_from_history

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data"
HN_TZ = timezone(timedelta(hours=-6))
ABBR_NORM = {"TBR": "TB", "CHW": "CWS", "KCR": "KC", "OAK": "ATH"}

FIELDNAMES = [
    "date",
    "away",
    "home",
    "side_con",
    "P",
    "cuota_modelo",
    "hora_HN",
    "game_pk",
]


def _norm(abbr: str) -> str:
    a = (abbr or "").upper()
    return ABBR_NORM.get(a, a)


def _parse_date(s: str | None) -> date:
    if s:
        return date.fromisoformat(s)
    return datetime.now(HN_TZ).date()


def export_predictions(
    target: date,
    *,
    min_minutes_before_start: int = 15,
    include_started: bool = False,
) -> Path:
    model, teams = train_model_from_history()
    abbr_map = {tid: v["abbr"].upper() for tid, v in teams.items()}
    client = MLBApiClient()
    now = datetime.now(timezone.utc)

    # Ventana UTC amplia: un día HN puede cruzar medianoche UTC
    start = (target - timedelta(days=1)).isoformat()
    end = (target + timedelta(days=1)).isoformat()
    data = client._get(
        "/schedule",
        params={"sportId": 1, "startDate": start, "endDate": end},
    )

    rows: list[dict] = []
    seen: set[int] = set()

    for day in data.get("dates", []):
        for g in day.get("games", []):
            gpk = int(g["gamePk"])
            if gpk in seen:
                continue

            gdt = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
            g_hn = gdt.astimezone(HN_TZ)
            if g_hn.date() != target:
                continue

            st = g.get("status", {})
            abs_state = st.get("abstractGameState")
            det = (st.get("detailedState") or "").lower()

            if not include_started:
                if abs_state != "Preview":
                    continue
                if "warmup" in det or "in progress" in det:
                    continue
                if gdt <= now + timedelta(minutes=min_minutes_before_start):
                    continue
            elif abs_state not in ("Preview", "Live", "Final"):
                continue

            away_t = g["teams"]["away"]["team"]
            home_t = g["teams"]["home"]["team"]
            aid = int(away_t["id"])
            hid = int(home_t["id"])
            pred = model.predict(hid, aid)

            a = _norm(away_t.get("abbreviation") or abbr_map.get(aid, "?"))
            h = _norm(home_t.get("abbreviation") or abbr_map.get(hid, "?"))

            if pred.home_win_prob >= pred.away_win_prob:
                side_con = "home"
                p = pred.home_win_prob
            else:
                side_con = "away"
                p = pred.away_win_prob

            seen.add(gpk)
            rows.append(
                {
                    "date": target.isoformat(),
                    "away": a,
                    "home": h,
                    "side_con": side_con,
                    "P": f"{p:.3f}",
                    "cuota_modelo": f"{(1.0 / p):.2f}",
                    "hora_HN": g_hn.strftime("%H:%M"),
                    "game_pk": gpk,
                }
            )

    rows.sort(key=lambda r: (r["hora_HN"], r["away"], r["home"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"predictions_{target.isoformat()}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Export daily Elo PRE-MATCH predictions CSV")
    ap.add_argument(
        "--date",
        help="Fecha HN YYYY-MM-DD (default: hoy Honduras)",
    )
    ap.add_argument(
        "--min-minutes",
        type=int,
        default=15,
        help="Margen PRE-MATCH antes del inicio (default 15)",
    )
    ap.add_argument(
        "--include-started",
        action="store_true",
        help="Incluir partidos ya iniciados/finalizados del día (debug)",
    )
    args = ap.parse_args()
    target = _parse_date(args.date)
    path = export_predictions(
        target,
        min_minutes_before_start=args.min_minutes,
        include_started=args.include_started,
    )
    n = sum(1 for _ in path.open(encoding="utf-8")) - 1
    print(f"OK {path} · {n} partidos · date={target.isoformat()}")
    print(f"WhatsApp: predicciones listas {target.isoformat()}")


if __name__ == "__main__":
    main()
