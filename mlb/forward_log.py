"""Registro de apuestas reales (forward test en Hondubet)."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from mlb.betting import DEFAULT_DECIMAL_ODDS, american_to_decimal
from mlb.config import DATA_DIR

FORWARD_CSV = DATA_DIR / "forward_bets.csv"
FIELDNAMES = [
    "logged_at",
    "game_date",
    "away",
    "home",
    "side",
    "stake",
    "decimal_odds",
    "american_odds",
    "result",
    "notes",
]


def _ensure_file(path: Path = FORWARD_CSV) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()


def log_bet(
    *,
    away: str,
    home: str,
    side: str,
    stake: float,
    decimal_odds: float | None = None,
    american_odds: float | None = None,
    game_date: str | None = None,
    result: str = "pending",
    notes: str = "",
) -> Path:
    """
    side: 'home' | 'away' | abreviatura del equipo
    result: pending | win | loss
    """
    side = side.strip().lower()
    if decimal_odds is None:
        if american_odds is not None:
            decimal_odds = american_to_decimal(american_odds)
        else:
            decimal_odds = DEFAULT_DECIMAL_ODDS

    _ensure_file()
    row = {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "game_date": game_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "away": away.upper(),
        "home": home.upper(),
        "side": side,
        "stake": f"{stake:.2f}",
        "decimal_odds": f"{decimal_odds:.3f}",
        "american_odds": "" if american_odds is None else str(american_odds),
        "result": result.lower(),
        "notes": notes,
    }
    with FORWARD_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(row)
    return FORWARD_CSV


def update_result(away: str, home: str, game_date: str, result: str) -> int:
    """Actualiza result de la ultima apuesta matching away/home/date."""
    if not FORWARD_CSV.exists():
        return 0
    result = result.lower()
    if result not in ("win", "loss", "pending"):
        raise ValueError("result debe ser win, loss o pending")

    with FORWARD_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    updated = 0
    for row in reversed(rows):
        if (
            row["away"].upper() == away.upper()
            and row["home"].upper() == home.upper()
            and row["game_date"] == game_date
            and row["result"] == "pending"
        ):
            row["result"] = result
            updated += 1
            break

    with FORWARD_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return updated
