from __future__ import annotations

from mlb.api import MLBApiClient
from mlb.config import DEFAULT_SEASONS
from mlb.database import get_connection, init_db, upsert_game, upsert_team, count_games


def fetch_seasons(seasons: list[int] | None = None) -> dict[str, int]:
    seasons = seasons or DEFAULT_SEASONS
    client = MLBApiClient()
    init_db()

    stats = {"teams": 0, "games": 0, "final_games": 0}

    with get_connection() as conn:
        for season in seasons:
            print(f"Descargando temporada {season}...")
            teams = client.fetch_teams(season)
            for team in teams:
                upsert_team(
                    conn,
                    team_id=team["id"],
                    name=team["name"],
                    abbreviation=team.get("abbreviation", "???"),
                )
            stats["teams"] = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]

            games = client.fetch_season_schedule(season)
            for game in games:
                status = game["status"]["abstractGameState"]
                home = game["teams"]["home"]
                away = game["teams"]["away"]

                home_score = home.get("score")
                away_score = away.get("score")
                home_win = None
                if status == "Final" and home_score is not None and away_score is not None:
                    if home_score != away_score:
                        home_win = 1 if home_score > away_score else 0
                    stats["final_games"] += 1

                upsert_game(
                    conn,
                    game_pk=game["gamePk"],
                    season=int(game["season"]),
                    game_date=game["gameDate"],
                    home_team_id=home["team"]["id"],
                    away_team_id=away["team"]["id"],
                    home_score=home_score,
                    away_score=away_score,
                    home_win=home_win,
                    status=status,
                )
                stats["games"] += 1

            conn.commit()
            print(f"  {season}: {len(games)} partidos procesados")

        stats["games"] = count_games(conn)

    return stats
