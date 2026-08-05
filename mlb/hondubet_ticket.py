"""OCR + parse de tickets Hondubet (capturas desde Telegram)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Alias OCR-friendly -> abreviatura MLB (orden: mas especifico primero)
_TEAM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"red\s*sox|boston|bosredsox|\bbos\b", re.I), "BOS"),
    (re.compile(r"yankees|new\s*york\s*y|\bnyy\b", re.I), "NYY"),
    (re.compile(r"mets|new\s*york\s*m|\bnym\b", re.I), "NYM"),
    (re.compile(r"dodgers|los\s*angeles\s*d|ladodgers|\blad\b", re.I), "LAD"),
    (re.compile(r"angels|los\s*angeles\s*a|laa|\banal\b", re.I), "LAA"),
    (re.compile(r"cubs|chicago\s*c|\bchc\b", re.I), "CHC"),
    (re.compile(r"white\s*sox|chicago\s*w|\bchw\b|\bcws\b", re.I), "CWS"),
    (re.compile(r"guardians|cleveland|\bcle\b", re.I), "CLE"),
    (re.compile(r"tigers|detroit|\bdet\b", re.I), "DET"),
    (re.compile(r"royals|kansas\s*city|\bkc\b|\bkcr\b", re.I), "KC"),
    (re.compile(r"twins|minnesota|\bmin\b", re.I), "MIN"),
    (re.compile(r"astros|houston|\bhou\b", re.I), "HOU"),
    (re.compile(r"athletics|\ba'?s\b|\bath\b|\boak\b", re.I), "ATH"),
    (re.compile(r"mariners|seattle|\bsea\b", re.I), "SEA"),
    (re.compile(r"rangers|texas|\btex\b", re.I), "TEX"),
    (re.compile(r"blue\s*jays|toronto|\btor\b", re.I), "TOR"),
    (re.compile(r"braves|atlanta|\batl\b", re.I), "ATL"),
    (re.compile(r"marlins|miami|\bmia\b", re.I), "MIA"),
    (re.compile(r"nationals|washington|\bwsh\b|\bwas\b", re.I), "WSH"),
    (re.compile(r"phillies|philadelphia|\bphi\b", re.I), "PHI"),
    (re.compile(r"brewers|milwaukee|\bmil\b", re.I), "MIL"),
    (re.compile(r"cardinals|st\.?\s*louis|\bstl\b", re.I), "STL"),
    (re.compile(r"pirates|pittsburgh|\bpit\b", re.I), "PIT"),
    (re.compile(r"reds|cincinnati|\bcin\b", re.I), "CIN"),
    (re.compile(r"padres|san\s*diego|\bsd\b|\bsdn\b", re.I), "SD"),
    (re.compile(r"giants|san\s*francisco|\bsf\b|\bsfg\b", re.I), "SF"),
    (re.compile(r"rockies|colorado|\bcol\b", re.I), "COL"),
    (re.compile(r"diamondbacks|arizona|\bari\b|\baz\b", re.I), "AZ"),
    (re.compile(r"rays|tampa|\btb\b|\btbr\b", re.I), "TB"),
    (re.compile(r"orioles|baltimore|\bbal\b", re.I), "BAL"),
]


@dataclass
class HondubetTicket:
    status: str  # win | loss | pending
    home: str
    away: str
    side: str  # home | away
    odds: float
    stake: float
    payout: float | None
    score: str | None
    ticket_id: str | None
    game_date: str | None
    raw_text: str

    @property
    def net_profit(self) -> float | None:
        if self.payout is None:
            return None
        if self.status == "win":
            return round(self.payout - self.stake, 2)
        if self.status == "loss":
            return round(-self.stake, 2)
        return None


def ocr_image(path: str | Path) -> str:
    """Extrae texto de la captura. Preferir RapidOCR (pip); fallback pytesseract."""
    path = Path(path)
    try:
        from rapidocr_onnxruntime import RapidOCR

        engine = RapidOCR()
        result, _ = engine(str(path))
        lines = [str(item[1]) for item in (result or [])]
        return "\n".join(lines)
    except Exception:
        pass

    try:
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(path), lang="eng+spa")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "No pude leer la imagen (OCR). Instala: pip install rapidocr-onnxruntime pillow"
        ) from exc


def _normalize_blob(text: str) -> str:
    t = text.replace("\u00a0", " ")
    t = t.replace("vs.", " vs ").replace("VS.", " vs ").replace("vs", " vs ")
    t = re.sub(r"([a-z])([A-Z])", r"\1 \2", t)
    t = re.sub(r"([A-Za-z])(\d)", r"\1 \2", t)
    t = re.sub(r"(\d)([A-Za-z])", r"\1 \2", t)
    t = re.sub(r"[^\w.:\-\s/]+", " ", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _find_teams(blob: str) -> tuple[str, str] | None:
    """Devuelve (home, away) segun orden de aparicion: local - visitante."""
    found: list[tuple[int, str]] = []
    used: set[str] = set()
    for pat, abbr in _TEAM_PATTERNS:
        m = pat.search(blob)
        if not m or abbr in used:
            continue
        found.append((m.start(), abbr))
        used.add(abbr)
    found.sort(key=lambda x: x[0])
    if len(found) < 2:
        return None
    home, away = found[0][1], found[1][1]
    return home, away


def _parse_status(blob: str) -> str:
    low = blob.lower()
    if re.search(r"\bganado\b|\bganada\b|\bwon\b", low):
        return "win"
    if re.search(r"\bperdido\b|\bperdida\b|\blost\b|\blose\b", low):
        return "loss"
    return "pending"


def _parse_money(blob: str, label: str) -> float | None:
    # Valor total HNL 25.00  /  Ganancia Total HNL 63.75
    m = re.search(
        rf"{label}\s*(?:hnl|l\.?|\$)?\s*([\d]+[.,]\d{{2}})",
        blob,
        flags=re.I,
    )
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def _parse_odds(blob: str) -> float | None:
    m = re.search(r"cuota\s*total\s*([\d]+[.,]\d{2,3})", blob, flags=re.I)
    if m:
        return float(m.group(1).replace(",", "."))
    # primer decimal tipo cuota (1.20 - 15.00) que no sea stake/payout grande
    for m in re.finditer(r"\b(\d{1,2}[.,]\d{2})\b", blob):
        val = float(m.group(1).replace(",", "."))
        if 1.01 <= val <= 50.0:
            return val
    return None


def _parse_score(blob: str) -> tuple[int, int] | None:
    m = re.search(r"resultado\s*(\d{1,2})\s*[:\-]\s*(\d{1,2})", blob, flags=re.I)
    if not m:
        m = re.search(r"\b(\d{1,2})\s*[:\-]\s*(\d{1,2})\b", blob)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _parse_selection(blob: str, score: tuple[int, int] | None, status: str) -> str | None:
    """1=local/home, 2=visitante/away. Si OCR no ve el digito, infiere del marcador."""
    # digito grande suelto cerca de cuota, evitando fechas/IDs
    for m in re.finditer(r"(?:^|\s)([12])(?:\s|$)", blob):
        # evita confundir con parte de "4:8" ya parseado
        return "home" if m.group(1) == "1" else "away"

    if score and status in ("win", "loss"):
        left, right = score
        if left == right:
            return None
        winner_side = "home" if left > right else "away"
        if status == "win":
            return winner_side
        return "away" if winner_side == "home" else "home"
    return None


def _parse_ticket_id(blob: str) -> str | None:
    m = re.search(r"\bid\s*[:#]?\s*(\d{6,})", blob, flags=re.I)
    return m.group(1) if m else None


def _parse_game_date(blob: str, year: int | None = None) -> str | None:
    """Honduras usa DD/MM. Devuelve YYYY-MM-DD."""
    m = re.search(r"\b(\d{2})[/.](\d{2})\b", blob)
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    if month > 12 and day <= 12:
        day, month = month, day
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    y = year or datetime.now().year
    return f"{y:04d}-{month:02d}-{day:02d}"


def parse_ticket_text(text: str, *, year: int | None = None) -> HondubetTicket:
    blob = _normalize_blob(text)
    teams = _find_teams(blob)
    if not teams:
        raise ValueError(
            "No pude detectar los equipos en la captura. "
            "Prueba otra foto o escribe: aposte BOS LAD away 2.55 25"
        )
    home, away = teams
    status = _parse_status(blob)
    score = _parse_score(blob)
    side = _parse_selection(blob, score, status)
    if not side:
        raise ValueError(
            "No pude detectar si apostaste 1 (local) o 2 (visitante). "
            "Reenvia la foto con caption: 1  o  2"
        )
    odds = _parse_odds(blob)
    stake = _parse_money(blob, r"valor\s*total")
    if stake is None:
        # a veces OCR pega HNL25.00 sin label cerca
        m = re.search(r"hnl\s*([\d]+[.,]\d{2})", blob, flags=re.I)
        stake = float(m.group(1).replace(",", ".")) if m else None
    payout = _parse_money(blob, r"ganancia\s*total")
    if odds is None:
        raise ValueError("No pude leer la cuota en la captura.")
    if stake is None:
        raise ValueError("No pude leer el stake (Valor total) en la captura.")

    score_txt = f"{score[0]}:{score[1]}" if score else None
    return HondubetTicket(
        status=status,
        home=home,
        away=away,
        side=side,
        odds=odds,
        stake=stake,
        payout=payout,
        score=score_txt,
        ticket_id=_parse_ticket_id(blob),
        game_date=_parse_game_date(blob, year=year),
        raw_text=blob,
    )


def parse_ticket_image(path: str | Path, *, caption: str = "", year: int | None = None) -> HondubetTicket:
    text = ocr_image(path)
    if caption.strip():
        text = f"{caption.strip()}\n{text}"
    # caption "1" / "2" ayuda si OCR no ve la seleccion
    return parse_ticket_text(text, year=year)


def format_ticket_summary(t: HondubetTicket) -> str:
    side_txt = "VISITANTE (2)" if t.side == "away" else "LOCAL (1)"
    status_txt = {"win": "GANADO", "loss": "PERDIDO", "pending": "PENDIENTE"}[t.status]
    lines = [
        f"Ticket interpretado: {status_txt}",
        f"{t.away} @ {t.home}",
        f"Lado: {side_txt} | Cuota: {t.odds} | Stake: L{t.stake:g}",
    ]
    if t.score:
        lines.append(f"Marcador: {t.score}")
    if t.payout is not None:
        lines.append(f"Paga: L{t.payout:g}")
    if t.net_profit is not None:
        sign = "+" if t.net_profit >= 0 else ""
        lines.append(f"Neto: {sign}L{t.net_profit:g}")
    if t.ticket_id:
        lines.append(f"ID Hondubet: {t.ticket_id}")
    if t.game_date:
        lines.append(f"Fecha: {t.game_date}")
    return "\n".join(lines)
