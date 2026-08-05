"""Escucha Telegram: actualizar / aposte / gane / perdi / fotos Hondubet."""

from __future__ import annotations

import os
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from mlb.bot import load_env_file, send_telegram
from mlb.forward_log import FORWARD_CSV, apply_hondubet_ticket, log_bet, settle_latest_pending, update_result
from mlb.hondubet_ticket import parse_ticket_image
from mlb.status_check import build_actualizar_message

load_env_file()

HELP_TEXT = """Bot MLB — comandos (celular)

ALERTAS automaticas: 10:00 y 16:00
Apuesta ideal: justo despues de la alerta, solo HOY, no EN VIVO

actualizar
  -> que SI / NO puedes apostar + value bets

aposte VISITANTE LOCAL lado cuota stake
  Ej: aposte BOS LAD away 2.55 25
  lado = away|home|1|2
  (1=local/home, 2=visitante/away)

gane VISITANTE LOCAL
perdi VISITANTE LOCAL
  Ej: gane BOS LAD

FOTO ticket Hondubet
  -> pega la captura del ticket (GANADO/PERDIDO o pendiente)
  -> el bot lee cuota, stake, equipos y actualiza el CSV
  Tip: si no detecta 1/2, caption de la foto: 1  o  2

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
            f"Cuando termine: pega la foto del ticket\n"
            f"o escribe: gane {away.upper()} {home.upper()}"
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
            n = settle_latest_pending(away, home, result)
        if n:
            return (
                f"Resultado actualizado: {away.upper()}@{home.upper()} -> {result}\n"
                f"Escribe: actualizar   (estado)\n"
                f"O en PC: python main.py evaluate"
            )
        return (
            f"No encontre apuesta pending de {away.upper()}@{home.upper()}.\n"
            f"Pega la foto del ticket Hondubet o:\n"
            f"aposte {away.upper()} {home.upper()} away 2.55 25"
        )

    return (
        "No entendi.\n\n"
        "Ejemplos:\n"
        "actualizar\n"
        "aposte BOS LAD away 2.55 25\n"
        "gane BOS LAD\n"
        "perdi BOS LAD\n"
        "(o pega foto del ticket Hondubet)\n"
        "ayuda"
    )


def _best_photo_file_id(msg: dict) -> str | None:
    photos = msg.get("photo") or []
    if photos:
        # ultimo = mayor resolucion
        return photos[-1].get("file_id")
    doc = msg.get("document") or {}
    mime = (doc.get("mime_type") or "").lower()
    if mime.startswith("image/") and doc.get("file_id"):
        return doc["file_id"]
    return None


def download_telegram_file(token: str, file_id: str, dest: Path) -> Path:
    meta = requests.get(
        f"https://api.telegram.org/bot{token}/getFile",
        params={"file_id": file_id},
        timeout=30,
    ).json()
    if not meta.get("ok"):
        raise RuntimeError(f"getFile fallo: {meta}")
    file_path = meta["result"]["file_path"]
    url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def handle_photo(token: str, file_id: str, caption: str = "") -> str:
    suffix = ".jpg"
    with tempfile.NamedTemporaryFile(prefix="hondubet_", suffix=suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        download_telegram_file(token, file_id, tmp_path)
        ticket = parse_ticket_image(tmp_path, caption=caption)
        return apply_hondubet_ticket(ticket)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def run_listener(*, poll_seconds: int = 3) -> None:
    token, allowed_chat = _token_chat()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    offset = 0
    print("Listener Telegram activo.")
    print("Comandos: actualizar | aposte ... | gane/perdi ... | FOTO ticket | ayuda")
    print(f"Forward CSV: {FORWARD_CSV}")
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
                if chat_id != allowed_chat:
                    continue

                text = (msg.get("text") or "").strip()
                caption = (msg.get("caption") or "").strip()
                file_id = _best_photo_file_id(msg)

                if file_id:
                    print(f"Foto recibida caption={caption!r}")
                    try:
                        reply = handle_photo(token, file_id, caption=caption)
                    except Exception as exc:  # noqa: BLE001
                        reply = f"No pude interpretar la foto.\n{exc}\n\nEscribe: ayuda"
                    send_telegram(reply, chat_id=chat_id)
                    print("Respondido (foto).")
                    continue

                if not text:
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
