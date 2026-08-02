import requests

from mlb.config import MLB_API_BASE


class MLBApiClient:
    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MLB-Predictor/1.0 (learning project)"})

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{MLB_API_BASE}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def fetch_teams(self, season: int) -> list[dict]:
        data = self._get("/teams", params={"sportId": 1, "season": season})
        return data.get("teams", [])

    def fetch_season_schedule(self, season: int, game_type: str = "R") -> list[dict]:
        data = self._get(
            "/schedule",
            params={"sportId": 1, "season": season, "gameType": game_type},
        )
        games: list[dict] = []
        for day in data.get("dates", []):
            games.extend(day.get("games", []))
        return games
