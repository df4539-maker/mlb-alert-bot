"""Bot de alertas: oportunidades de value bet para operar manual en Hondubet."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from mlb.betting import DEFAULT_AMERICAN_ODDS
from mlb.config import BASE_DIR, DATA_DIR
from mlb.predict import predict_upcoming

SIGNALS_CSV = DATA_DIR / "signals_log.csv"


def load_env_file(path: Path | None = None) -> None:
    """Carga variables desde .env sin dependencia extra."""
    env_path = path or (BASE_DIR / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()


def format_alert(signal: dict, stake_units: float = 1.0) -> str:
    start = signal.get("start_utc", signal.get("date", "?"))
    mins = signal.get("minutes_to_start")
    timing = f"Inicio UTC {start}"
    if mins is not None:
        timing += f" (en ~{mins} min)"

    away_label = signal.get("away_label") or signal["away"]
    home_label = signal.get("home_label") or signal["home"]
    matchup = f"{away_label}\n  @ {home_label}"

    if signal.get("value_bet") not in ("home", "away"):
        return (
            f"MLB | {matchup}\n"
            f"{timing}\n"
            f"Modelo: Local {signal['home_prob_pct']:.1f}% | Visitante {signal['away_prob_pct']:.1f}%\n"
            f"Sin value (edge < minimo vs {DEFAULT_AMERICAN_ODDS})"
        )

    side_label = "LOCAL" if signal["value_bet"] == "home" else "VISITANTE"
    team_label = home_label if signal["value_bet"] == "home" else away_label
    return (
        f"VALUE BET | MLB | PRE-MATCH\n"
        f"{matchup}\n"
        f"{timing}\n"
        f"Estado: {signal.get('status', 'Preview')} — OK para apostar\n"
        f"Modelo: Local {signal['home_prob_pct']:.1f}% | Visitante {signal['away_prob_pct']:.1f}%\n"
        f"Mercado ref: {signal['market_implied_pct']:.1f}% ({DEFAULT_AMERICAN_ODDS})\n"
        f"Edge: +{signal['edge_pct']:.1f}% -> APOSTAR {side_label}\n"
        f"Equipo: {team_label}\n"
        f"Stake sugerido: {stake_units:.0f}u (ej. L5)\n"
        f"Si en Hondubet ya dice EN VIVO -> NO apostar"
    )


def format_digest(signals: list[dict], stake_units: float = 1.0) -> str:
    if not signals:
        return (
            "BOT MLB | Sin value bets PRE-MATCH\n"
            f"(solo partidos no iniciados; edge vs {DEFAULT_AMERICAN_ODDS})"
        )

    lines = [
        f"BOT MLB | {len(signals)} PRE-MATCH (no iniciados)",
        f"Fecha bot: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        "Regla: si el partido ya empezo -> NO apostar",
        "-" * 40,
    ]
    for s in signals:
        lines.append(format_alert(s, stake_units=stake_units))
        lines.append("-" * 40)
    lines.append("Cuotas simuladas. Confirma en Hondubet (solo pre-partido).")
    return "\n".join(lines)


def log_signals(signals: list[dict], path: Path | None = None) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = path or SIGNALS_CSV
    fieldnames = [
        "logged_at",
        "date",
        "away",
        "home",
        "value_bet",
        "home_prob_pct",
        "away_prob_pct",
        "edge_pct",
        "market_implied_pct",
        "stake_units",
    ]
    write_header = not out.exists()
    logged_at = datetime.now(timezone.utc).isoformat()

    with out.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for s in signals:
            writer.writerow(
                {
                    "logged_at": logged_at,
                    "date": s["date"],
                    "away": s["away"],
                    "home": s["home"],
                    "value_bet": s["value_bet"],
                    "home_prob_pct": s["home_prob_pct"],
                    "away_prob_pct": s["away_prob_pct"],
                    "edge_pct": s["edge_pct"],
                    "market_implied_pct": s["market_implied_pct"],
                    "stake_units": 1.0,
                }
            )
    return out


def send_telegram(message: str, token: str | None = None, chat_id: str | None = None) -> bool:
    token = token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # Telegram limita a 4096 caracteres por mensaje
    chunks: list[str] = []
    if len(message) <= 4000:
        chunks = [message]
    else:
        current: list[str] = []
        size = 0
        for block in message.split("\n----------------------------------------\n"):
            piece = block if not current else "\n----------------------------------------\n" + block
            if size + len(piece) > 3900 and current:
                chunks.append("".join(current))
                current = [block]
                size = len(block)
            else:
                current.append(piece if current else block)
                size += len(piece if current else block)
        if current:
            chunks.append("".join(current))

    for chunk in chunks:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": chunk},
            timeout=30,
        )
        response.raise_for_status()
    return True


def run_bot(
    *,
    days_ahead: int = 3,
    min_edge: float = 0.03,
    stake_units: float = 1.0,
    only_value: bool = True,
    send_to_telegram: bool = False,
    min_minutes_before_start: int = 15,
) -> list[dict]:
    """Genera alertas, las imprime, las guarda en CSV y opcionalmente Telegram."""
    preds = predict_upcoming(
        days_ahead=days_ahead,
        min_edge=min_edge,
        min_minutes_before_start=min_minutes_before_start,
    )
    signals = [p for p in preds if p.get("value_bet") in ("home", "away")] if only_value else preds

    message = format_digest(signals, stake_units=stake_units)
    print(message)

    if signals:
        path = log_signals(signals)
        print(f"\nLog guardado: {path}")
    else:
        print("\nSin senales para guardar en log.")

    if send_to_telegram:
        try:
            ok = send_telegram(message)
            if ok:
                print("Enviado a Telegram.")
            else:
                print(
                    "Telegram no configurado. Define TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID "
                    "o corre sin --telegram."
                )
        except requests.RequestException as exc:
            print(f"Error enviando a Telegram: {exc}")

    return signals
