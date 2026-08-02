"""Chequeo rapido de estado de partidos alertados."""
from datetime import datetime, timedelta, timezone

import requests

from mlb.bot import format_digest, send_telegram
from mlb.predict import predict_upcoming

WATCH = [
    ("BOS", "LAD"),
    ("DET", "ATH"),
    ("DET", "OAK"),
    ("MIN", "SEA"),
    ("PIT", "MIL"),
    ("STL", "NYY"),
    ("LAD", "CHC"),
    ("TB", "COL"),
]


def main() -> None:
    now = datetime.now(timezone.utc)
    start = now.strftime("%Y-%m-%d")
    end = (now + timedelta(days=3)).strftime("%Y-%m-%d")
    teams = requests.get(
        "https://statsapi.mlb.com/api/v1/teams",
        params={"sportId": 1, "season": now.year},
        timeout=30,
    ).json()["teams"]
    id2abbr = {t["id"]: t["abbreviation"] for t in teams}

    schedule = requests.get(
        "https://statsapi.mlb.com/api/v1/schedule",
        params={"sportId": 1, "startDate": start, "endDate": end},
        timeout=60,
    ).json()

    print("=== ESTADO ACTUAL (alertas previas) ===")
    print(f"Ahora UTC: {now.strftime('%Y-%m-%d %H:%M')}")
    openable = []
    closed = []
    for day in schedule.get("dates", []):
        for g in day["games"]:
            away = id2abbr.get(g["teams"]["away"]["team"]["id"], "?")
            home = id2abbr.get(g["teams"]["home"]["team"]["id"], "?")
            if (away, home) not in WATCH:
                continue
            st = g["status"]
            abstract = st.get("abstractGameState")
            detailed = st.get("detailedState")
            gdt = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
            mins = (gdt - now).total_seconds() / 60.0
            line = f"{away}@{home} | {g['gameDate'][:16]} | {abstract}/{detailed}"
            if abstract == "Preview" and mins > 5:
                openable.append(line + f" | en {mins:.0f} min -> SI puedes apostar")
            else:
                closed.append(line + " -> NO apostar (ya inicio o no Preview)")

    print("\n-- AUN NO INICIAN (puedes apostar) --")
    for x in openable or ["(ninguno de la lista previa)"]:
        print(x)
    print("\n-- YA INICIARON / NO VALIDOS --")
    for x in closed or ["(ninguno)"]:
        print(x)

    print("\n=== ALERTAS NUEVAS (solo Preview, bot actualizado) ===")
    preds = predict_upcoming(days_ahead=2, min_edge=0.03)
    signals = [p for p in preds if p.get("value_bet") in ("home", "away")]
    msg = format_digest(signals, stake_units=1.0)
    print(msg)
    try:
        if send_telegram(msg):
            print("\nEnviado a Telegram.")
    except Exception as exc:  # noqa: BLE001
        print(f"Telegram: {exc}")


if __name__ == "__main__":
    main()
