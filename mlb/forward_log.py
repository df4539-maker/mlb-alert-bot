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


def ticket_already_logged(ticket_id: str) -> bool:
    if not ticket_id or not FORWARD_CSV.exists():
        return False
    needle = f"ticket={ticket_id}"
    with FORWARD_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if needle in (row.get("notes") or ""):
                return True
    return False


def settle_latest_pending(away: str, home: str, result: str) -> int:
    """Marca win/loss en el pending mas reciente de ese matchup (cualquier fecha)."""
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
            and row["result"] == "pending"
        ):
            row["result"] = result
            updated = 1
            break

    if updated:
        with FORWARD_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
    return updated


def apply_hondubet_ticket(ticket) -> str:
    """
    Registra o liquida segun captura Hondubet.
    Devuelve mensaje corto de lo hecho en el CSV.
    """
    from mlb.hondubet_ticket import HondubetTicket, format_ticket_summary

    if not isinstance(ticket, HondubetTicket):
        raise TypeError("ticket debe ser HondubetTicket")

    if ticket.ticket_id and ticket_already_logged(ticket.ticket_id):
        return (
            format_ticket_summary(ticket)
            + f"\n\nYa estaba registrado (ticket={ticket.ticket_id}). No duplique."
        )

    notes_parts = ["desde foto Hondubet"]
    if ticket.ticket_id:
        notes_parts.append(f"ticket={ticket.ticket_id}")
    if ticket.score:
        notes_parts.append(f"score={ticket.score}")
    if ticket.payout is not None:
        notes_parts.append(f"payout={ticket.payout:g}")
    notes = "; ".join(notes_parts)

    action = ""
    if ticket.status in ("win", "loss"):
        n = 0
        if ticket.game_date:
            n = update_result(ticket.away, ticket.home, ticket.game_date, ticket.status)
        if not n:
            n = settle_latest_pending(ticket.away, ticket.home, ticket.status)
        if n:
            action = f"Actualizado pending -> {ticket.status}"
        else:
            log_bet(
                away=ticket.away,
                home=ticket.home,
                side=ticket.side,
                stake=ticket.stake,
                decimal_odds=ticket.odds,
                game_date=ticket.game_date,
                result=ticket.status,
                notes=notes,
            )
            action = f"Registrado como {ticket.status} (no habia pending)"
    else:
        log_bet(
            away=ticket.away,
            home=ticket.home,
            side=ticket.side,
            stake=ticket.stake,
            decimal_odds=ticket.odds,
            game_date=ticket.game_date,
            result="pending",
            notes=notes,
        )
        action = "Registrado pending"

    return format_ticket_summary(ticket) + f"\n\nCSV: {action}\nArchivo: {FORWARD_CSV.name}"
