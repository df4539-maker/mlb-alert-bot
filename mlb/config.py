from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mlb.db"

MLB_API_BASE = "https://statsapi.mlb.com/api/v1"
DEFAULT_SEASONS = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

# Elo parameters (tunable after backtest review)
INITIAL_ELO = 1500.0
K_FACTOR = 20.0
HOME_ADVANTAGE = 35.0
