from __future__ import annotations

import math
from dataclasses import dataclass

from mlb.config import HOME_ADVANTAGE, INITIAL_ELO, K_FACTOR


def expected_score(rating_a: float, rating_b: float, home_advantage: float = 0.0) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a + home_advantage) / 400.0))


@dataclass
class EloPrediction:
    home_win_prob: float
    away_win_prob: float
    home_elo: float
    away_elo: float


class EloModel:
    def __init__(
        self,
        initial_rating: float = INITIAL_ELO,
        k_factor: float = K_FACTOR,
        home_advantage: float = HOME_ADVANTAGE,
    ) -> None:
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.ratings: dict[int, float] = {}

    def get_rating(self, team_id: int) -> float:
        return self.ratings.get(team_id, self.initial_rating)

    def predict(self, home_team_id: int, away_team_id: int) -> EloPrediction:
        home_elo = self.get_rating(home_team_id)
        away_elo = self.get_rating(away_team_id)
        home_win_prob = expected_score(home_elo, away_elo, self.home_advantage)
        return EloPrediction(
            home_win_prob=home_win_prob,
            away_win_prob=1.0 - home_win_prob,
            home_elo=home_elo,
            away_elo=away_elo,
        )

    def update(self, home_team_id: int, away_team_id: int, home_win: int) -> None:
        home_elo = self.get_rating(home_team_id)
        away_elo = self.get_rating(away_team_id)

        expected_home = expected_score(home_elo, away_elo, self.home_advantage)
        expected_away = 1.0 - expected_home

        actual_home = float(home_win)
        actual_away = 1.0 - actual_home

        new_home = home_elo + self.k_factor * (actual_home - expected_home)
        new_away = away_elo + self.k_factor * (actual_away - expected_away)

        self.ratings[home_team_id] = new_home
        self.ratings[away_team_id] = new_away

    def reset(self) -> None:
        self.ratings.clear()


def log_loss(probability: float, actual: int, eps: float = 1e-15) -> float:
    p = min(max(probability, eps), 1.0 - eps)
    return -(actual * math.log(p) + (1 - actual) * math.log(1 - p))


def brier_score(probability: float, actual: int) -> float:
    return (probability - actual) ** 2
