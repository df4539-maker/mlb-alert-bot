import sqlite3
from pathlib import Path

from mlb.config import DB_PATH, DATA_DIR


SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS games (
    game_pk INTEGER PRIMARY KEY,
    season INTEGER NOT NULL,
    game_date TEXT NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    home_win INTEGER,
    status TEXT NOT NULL,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

CREATE INDEX IF NOT EXISTS idx_games_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_games_season ON games(season);
"""


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_team(conn: sqlite3.Connection, team_id: int, name: str, abbreviation: str) -> None:
    conn.execute(
        """
        INSERT INTO teams (team_id, name, abbreviation)
        VALUES (?, ?, ?)
        ON CONFLICT(team_id) DO UPDATE SET
            name = excluded.name,
            abbreviation = excluded.abbreviation
        """,
        (team_id, name, abbreviation),
    )


def upsert_game(
    conn: sqlite3.Connection,
    *,
    game_pk: int,
    season: int,
    game_date: str,
    home_team_id: int,
    away_team_id: int,
    home_score: int | None,
    away_score: int | None,
    home_win: int | None,
    status: str,
) -> None:
    conn.execute(
        """
        INSERT INTO games (
            game_pk, season, game_date, home_team_id, away_team_id,
            home_score, away_score, home_win, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_pk) DO UPDATE SET
            season = excluded.season,
            game_date = excluded.game_date,
            home_team_id = excluded.home_team_id,
            away_team_id = excluded.away_team_id,
            home_score = excluded.home_score,
            away_score = excluded.away_score,
            home_win = excluded.home_win,
            status = excluded.status
        """,
        (
            game_pk,
            season,
            game_date,
            home_team_id,
            away_team_id,
            home_score,
            away_score,
            home_win,
            status,
        ),
    )


def count_games(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS n FROM games").fetchone()
    return int(row["n"])


def fetch_final_games(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            game_pk,
            season,
            game_date,
            home_team_id,
            away_team_id,
            home_score,
            away_score,
            home_win
        FROM games
        WHERE status = 'Final'
          AND home_win IS NOT NULL
        ORDER BY game_date ASC, game_pk ASC
        """
    ).fetchall()
