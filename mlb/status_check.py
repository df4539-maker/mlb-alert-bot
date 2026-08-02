"""Revisa si alertas siguen siendo apostables + responde 'actualizar' desde Telegram."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from mlb.api import MLBApiClient
from mlb.bot import format_digest, send_telegram
from mlb.database import get_connection, init_db
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


def _team_maps() -> tuple[dict[int, str], dict[int, str]]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT team_id, abbreviation, name FROM teams").fetchall()
    abbr = {int(r["team_id"]): r["abbreviation"] for r in rows}
    names = {int(r["team_id"]): r["name"] for r in rows}
    return abbr, names


def check_watched_games() -> tuple[list[str], list[str]]:
    now = datetime.now(timezone.utc)
    client = MLBApiClient()
    id2abbr, id2name = _team_maps()

    start = now.strftime("%Y-%m-%d")
    end = (now + timedelta(days=3)).strftime("%Y-%m-%d")
    data = client._get(
        "/schedule",
        params={"sportId": 1, "startDate": start, "endDate": end},
    )

    openable: list[str] = []
    closed: list[str] = []
    for day in data.get("dates", []):
        for g in day.get("games", []):
            away_id = g["teams"]["away"]["team"]["id"]
            home_id = g["teams"]["home"]["team"]["id"]
            away = id2abbr.get(away_id, "?")
            home = id2abbr.get(home_id, "?")
            if (away, home) not in WATCH:
                continue
            away_name = id2name.get(away_id, away)
            home_name = id2name.get(home_id, home)
            st = g["status"]
            abstract = st.get("abstractGameState")
            detailed = st.get("detailedState")
            gdt = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
            mins = (gdt - now).total_seconds() / 60.0
            label = f"{away} ({away_name}) @ {home} ({home_name})"
            when = g["gameDate"][:16].replace("T", " ")
            if abstract == "Preview" and mins > 15:
                openable.append(f"SI apostar | {label}\n  {when} UTC | {detailed} | en ~{mins:.0f} min")
            else:
                closed.append(
                    f"NO apostar | {label}\n  {when} UTC | {detailed} | estado={abstract}"
                )
    return openable, closed


def build_actualizar_message() -> str:
    """Mensaje completo para cuando el usuario escribe 'actualizar' en Telegram."""
    openable, closed = check_watched_games()
    lines = [
        "ACTUALIZAR | estado de alertas",
        f"Ahora: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        "",
        "== AUN NO INICIAN (SI puedes apostar) ==",
    ]
    lines.extend(openable or ["(ninguno)"])
    lines.append("")
    lines.append("== YA INICIARON (NO apostar) ==")
    lines.extend(closed or ["(ninguno)"])
    lines.append("")
    lines.append("== VALUE BETS PRE-MATCH AHORA ==")

    preds = predict_upcoming(days_ahead=2, min_edge=0.03)
    signals = [p for p in preds if p.get("value_bet") in ("home", "away")]
    digest = format_digest(signals, stake_units=1.0)
    return "\n".join(lines) + "\n\n" + digest


def print_status(*, send_to_telegram: bool = False) -> None:
    message = build_actualizar_message()
    print(message)
    if send_to_telegram:
        try:
            if send_telegram(message):
                print("\nEnviado a Telegram.")
            else:
                print("\nTelegram no configurado.")
        except requests.RequestException as exc:
            print(f"\nError Telegram: {exc}")
