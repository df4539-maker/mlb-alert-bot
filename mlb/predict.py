"""Predicciones para partidos próximos (después de entrenar con histórico)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mlb.api import MLBApiClient
from mlb.betting import DEFAULT_DECIMAL_ODDS, decimal_to_implied_prob, has_value
from mlb.database import fetch_final_games, get_connection, init_db
from mlb.elo import EloModel

# No alertar partidos que empiezan en menos de N minutos (evita live/warmup)
MIN_MINUTES_BEFORE_START = 15


def train_model_from_history() -> tuple[EloModel, dict[int, dict[str, str]]]:
    init_db()
    model = EloModel()
    with get_connection() as conn:
        games = fetch_final_games(conn)
        teams = {
            int(row["team_id"]): {
                "abbr": row["abbreviation"],
                "name": row["name"],
            }
            for row in conn.execute("SELECT team_id, abbreviation, name FROM teams")
        }

    for game in games:
        model.update(game["home_team_id"], game["away_team_id"], int(game["home_win"]))

    return model, teams


def _team_label(teams: dict[int, dict[str, str]], team_id: int) -> tuple[str, str, str]:
    info = teams.get(team_id, {})
    abbr = info.get("abbr", str(team_id))
    name = info.get("name", abbr)
    return abbr, name, f"{abbr} ({name})"


def _is_prematch(game: dict, now: datetime, min_minutes: int = MIN_MINUTES_BEFORE_START) -> bool:
    """Solo partidos que aun no empiezan (Preview) y con margen de tiempo."""
    status = game.get("status", {})
    if status.get("abstractGameState") != "Preview":
        return False
    detailed = (status.get("detailedState") or "").lower()
    if "warmup" in detailed or "in progress" in detailed:
        return False

    game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00"))
    if game_date <= now + timedelta(minutes=min_minutes):
        return False
    return True


def predict_upcoming(
    days_ahead: int = 3,
    min_edge: float = 0.03,
    *,
    min_minutes_before_start: int = MIN_MINUTES_BEFORE_START,
) -> list[dict]:
    model, teams = train_model_from_history()
    client = MLBApiClient()
    season = datetime.now(timezone.utc).year

    schedule = client.fetch_season_schedule(season)
    market_implied = decimal_to_implied_prob(DEFAULT_DECIMAL_ODDS)
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=days_ahead)
    predictions: list[dict] = []

    for game in schedule:
        if not _is_prematch(game, now, min_minutes_before_start):
            continue

        game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00"))
        if game_date > horizon:
            continue

        home_id = game["teams"]["home"]["team"]["id"]
        away_id = game["teams"]["away"]["team"]["id"]
        pred = model.predict(home_id, away_id)

        home_abbr, home_name, home_label = _team_label(teams, home_id)
        away_abbr, away_name, away_label = _team_label(teams, away_id)

        value_bet = None
        edge = 0.0
        if has_value(pred.home_win_prob, market_implied, min_edge):
            value_bet = "home"
            edge = pred.home_win_prob - market_implied
        elif has_value(pred.away_win_prob, market_implied, min_edge):
            value_bet = "away"
            edge = pred.away_win_prob - market_implied

        mins_to_start = (game_date - now).total_seconds() / 60.0
        predictions.append(
            {
                "game_pk": game["gamePk"],
                "date": game["gameDate"][:10],
                "start_utc": game["gameDate"][:16].replace("T", " "),
                "minutes_to_start": int(mins_to_start),
                "status": game["status"].get("detailedState", "Preview"),
                "bettable": True,
                "home": home_abbr,
                "away": away_abbr,
                "home_name": home_name,
                "away_name": away_name,
                "home_label": home_label,
                "away_label": away_label,
                "home_prob": pred.home_win_prob,
                "away_prob": pred.away_win_prob,
                "home_prob_pct": round(pred.home_win_prob * 100, 1),
                "away_prob_pct": round(pred.away_win_prob * 100, 1),
                "market_implied_pct": round(market_implied * 100, 1),
                "edge_pct": round(edge * 100, 1),
                "value_bet": value_bet or "-",
            }
        )

    return sorted(predictions, key=lambda x: (x["date"], x["minutes_to_start"], x["away"]))


def print_upcoming(min_edge: float = 0.03) -> None:
    preds = predict_upcoming(min_edge=min_edge)
    if not preds:
        print("No hay partidos proximos en estado Preview (no iniciados).")
        return

    print("\n=== PROXIMOS PARTIDOS MLB (solo NO iniciados) ===")
    for p in preds:
        print(
            f"{p['start_utc']} (+{p['minutes_to_start']} min) | "
            f"{p['away_label']} @ {p['home_label']} | "
            f"L {p['home_prob_pct']}% V {p['away_prob_pct']}% | value={p['value_bet']}"
        )
    print("\nSolo pre-match. Si el partido ya inicio en Hondubet -> NO apostar.")
