"""Escucha Telegram: actualizar / aposte / gane / perdi."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone

import requests

from mlb.bot import load_env_file, send_telegram
from mlb.forward_log import FORWARD_CSV, log_bet, update_result
from mlb.status_check import build_actualizar_message

load_env_file()

HELP_TEXT = """Bot MLB — comandos (celular)

ALERTAS automaticas: 10:00 y 16:00
Apuesta ideal: justo despues de la alerta, solo HOY, no EN VIVO

actualizar
  -> que SI / NO puedes apostar + value bets

aposte VISITANTE LOCAL lado cuota stake
  Ej: aposte BOS LAD away 2.55 5
  lado = away|home|1|2
  (1=local/home, 2=visitante/away)

gane VISITANTE LOCAL
perdi VISITANTE LOCAL
  Ej: gane BOS LAD

hola / ayuda
  -> este mensaje
"""


def _token_chat() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env")
    return token, chat_id


def _parse_side(raw: str) -> str:
    s = raw.strip().lower()
    if s in ("1", "home", "local", "h"):
        return "home"
    if s in ("2", "away", "visitante", "v", "a"):
        return "away"
    return s


def handle_message(text: str) -> str:
    raw = text.strip()
    low = raw.lower()

    if low in ("hola", "help", "ayuda", "/start", "/help"):
        return HELP_TEXT

    if low in ("actualizar", "/actualizar", "update", "/update", "status", "/status") or low.startswith(
        "actualizar"
    ):
        return build_actualizar_message()

    # aposte BOS LAD away 2.55 5
    # aposte BOS@LAD 2 2.55 5
    m = re.match(
        r"^(?:aposte|apost[eé]|confirmo|jugue|jugu[eé])\s+"
        r"([A-Za-z]{2,4})\s*[@\s]\s*([A-Za-z]{2,4})\s+"
        r"(\d|away|home|local|visitante|h|a|v)\s+"
        r"([\d.]+)\s+"
        r"([\d.]+)\s*$",
        low,
        flags=re.IGNORECASE,
    )
    if m:
        away, home, side_raw, odds_s, stake_s = m.groups()
        side = _parse_side(side_raw)
        odds = float(odds_s)
        stake = float(stake_s)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = log_bet(
            away=away,
            home=home,
            side=side,
            stake=stake,
            decimal_odds=odds,
            game_date=today,
            result="pending",
            notes="confirmado por Telegram",
        )
        side_txt = "VISITANTE" if side == "away" else "LOCAL" if side == "home" else side
        return (
            f"Operacion registrada\n"
            f"{away.upper()} @ {home.upper()}\n"
            f"Lado: {side_txt} | Cuota: {odds} | Stake: L{stake:g}\n"
            f"Estado: pending\n"
            f"Archivo: {path.name}\n\n"
            f"Cuando termine escribe:\n"
            f"gane {away.upper()} {home.upper()}\n"
            f"o: perdi {away.upper()} {home.upper()}"
        )

    # gane BOS LAD  /  perdi BOS LAD
    m2 = re.match(
        r"^(gane|gan[eé]|win|perdi|perd[ií]|loss)\s+([A-Za-z]{2,4})\s+([A-Za-z]{2,4})\s*$",
        low,
    )
    if m2:
        word, away, home = m2.groups()
        result = "win" if word.startswith("gan") or word == "win" else "loss"
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        n = update_result(away, home, today, result)
        if not n:
            # intenta sin filtrar solo hoy: busca pending mas reciente de ese matchup
            n = _settle_latest(away, home, result)
        if n:
            return (
                f"Resultado actualizado: {away.upper()}@{home.upper()} -> {result}\n"
                f"Escribe: actualizar   (estado)\n"
                f"O en PC: python main.py evaluate"
            )
        return (
            f"No encontre apuesta pending de {away.upper()}@{home.upper()}.\n"
            f"Primero: aposte {away.upper()} {home.upper()} away 2.55 5"
        )

    return (
        "No entendi.\n\n"
        "Ejemplos:\n"
        "actualizar\n"
        "aposte BOS LAD away 2.55 5\n"
        "gane BOS LAD\n"
        "perdi BOS LAD\n"
        "ayuda"
    )


def _settle_latest(away: str, home: str, result: str) -> int:
    if not FORWARD_CSV.exists():
        return 0
    import csv

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
        from mlb.forward_log import FIELDNAMES

        with FORWARD_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            w.writerows(rows)
    return updated


def run_listener(*, poll_seconds: int = 3) -> None:
    token, allowed_chat = _token_chat()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    offset = 0
    print("Listener Telegram activo.")
    print("Comandos: actualizar | aposte ... | gane/perdi ... | ayuda")
    print("Ctrl+C para detener.\n")

    boot = requests.get(url, params={"timeout": 0}, timeout=30).json()
    if boot.get("ok"):
        for item in boot.get("result", []):
            offset = max(offset, int(item["update_id"]) + 1)

    while True:
        try:
            resp = requests.get(
                url,
                params={"offset": offset, "timeout": 25},
                timeout=35,
            )
            data = resp.json()
            if not data.get("ok"):
                time.sleep(poll_seconds)
                continue

            for item in data.get("result", []):
                offset = max(offset, int(item["update_id"]) + 1)
                msg = item.get("message") or {}
                chat = msg.get("chat") or {}
                chat_id = str(chat.get("id", ""))
                text = (msg.get("text") or "").strip()
                if not text or chat_id != allowed_chat:
                    continue

                print(f"Msg: {text!r}")
                try:
                    reply = handle_message(text)
                except Exception as exc:  # noqa: BLE001
                    reply = f"Error: {exc}"
                send_telegram(reply, chat_id=chat_id)
                print("Respondido.")

        except requests.RequestException as exc:
            print(f"Error de red: {exc}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nListener detenido.")
            break


if __name__ == "__main__":
    run_listener()
