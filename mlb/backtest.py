from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from mlb.betting import (
    DEFAULT_DECIMAL_ODDS,
    DEFAULT_VIG,
    bet_payout,
    decimal_to_implied_prob,
    has_value,
    market_odds_from_prob,
)
from mlb.config import DATA_DIR, INITIAL_ELO
from mlb.database import fetch_final_games, get_connection, init_db
from mlb.elo import EloModel, brier_score, log_loss


@dataclass
class BettingResult:
    bets_placed: int
    bets_won: int
    hit_rate: float
    total_staked: float
    net_profit: float
    roi: float
    max_drawdown: float
    min_edge_used: float


@dataclass
class BacktestResult:
    mode: str
    total_games: int
    correct: int
    accuracy: float
    avg_log_loss: float
    avg_brier: float
    home_win_rate: float
    baseline_accuracy: float
    by_season: dict[int, dict[str, float]]
    betting: BettingResult | None = None
    calibration: list[dict[str, float]] = field(default_factory=list)


def _evaluate_games(
    games: list,
    model: EloModel,
    *,
    update_after: bool = True,
    min_edge: float | None = None,
    stake: float = 1.0,
    simulate_betting: bool = False,
) -> tuple[dict, list[dict], BettingResult | None]:
    correct = 0
    total_log_loss = 0.0
    total_brier = 0.0
    home_wins = 0
    season_stats: dict[int, dict[str, float]] = defaultdict(
        lambda: {"games": 0, "correct": 0, "log_loss": 0.0}
    )
    calibration_buckets: dict[str, list[int]] = defaultdict(list)
    rows: list[dict] = []

    bets_placed = bets_won = 0
    total_staked = 0.0
    net_profit = 0.0
    bankroll_curve = [0.0]
    market_implied = decimal_to_implied_prob(DEFAULT_DECIMAL_ODDS)

    for game in games:
        home_win = int(game["home_win"])
        home_wins += home_win
        season = int(game["season"])

        pred = model.predict(game["home_team_id"], game["away_team_id"])
        predicted_home = pred.home_win_prob >= 0.5
        actual_home = home_win == 1
        if predicted_home == actual_home:
            correct += 1

        ll = log_loss(pred.home_win_prob, home_win)
        bs = brier_score(pred.home_win_prob, home_win)
        total_log_loss += ll
        total_brier += bs

        season_stats[season]["games"] += 1
        if predicted_home == actual_home:
            season_stats[season]["correct"] += 1
        season_stats[season]["log_loss"] += ll

        bucket = f"{int(pred.home_win_prob * 10) * 10}-{int(pred.home_win_prob * 10) * 10 + 10}%"
        calibration_buckets[bucket].append(home_win)

        bet_side = None
        bet_won = None
        profit = 0.0

        if simulate_betting and min_edge is not None:
            # Mercado simulado: línea fija -110/-110 (típica MLB moneyline cercana)
            home_market = market_implied
            away_market = market_implied

            if has_value(pred.home_win_prob, home_market, min_edge):
                bet_side = "home"
                bet_won = home_win == 1
            elif has_value(pred.away_win_prob, away_market, min_edge):
                bet_side = "away"
                bet_won = home_win == 0

            if bet_side:
                bets_placed += 1
                total_staked += stake
                profit = bet_payout(stake, bet_won)
                net_profit += profit
                if bet_won:
                    bets_won += 1
                bankroll_curve.append(bankroll_curve[-1] + profit)

        rows.append(
            {
                "game_pk": game["game_pk"],
                "season": season,
                "game_date": game["game_date"],
                "home_team_id": game["home_team_id"],
                "away_team_id": game["away_team_id"],
                "home_win_prob": round(pred.home_win_prob, 4),
                "away_win_prob": round(pred.away_win_prob, 4),
                "home_win": home_win,
                "correct": int(predicted_home == actual_home),
                "log_loss": round(ll, 4),
                "bet_side": bet_side or "",
                "bet_won": "" if bet_won is None else int(bet_won),
                "profit": round(profit, 4),
            }
        )

        if update_after:
            model.update(game["home_team_id"], game["away_team_id"], home_win)

    total = len(games)
    home_win_rate = home_wins / total if total else 0.0
    baseline_accuracy = max(home_win_rate, 1 - home_win_rate)

    by_season = {}
    for s, stats in sorted(season_stats.items()):
        g = int(stats["games"])
        by_season[s] = {
            "games": g,
            "accuracy": stats["correct"] / g,
            "avg_log_loss": stats["log_loss"] / g,
        }

    calibration = []
    for label in sorted(calibration_buckets.keys()):
        outcomes = calibration_buckets[label]
        calibration.append(
            {
                "bucket": label,
                "games": len(outcomes),
                "actual_home_win_rate": sum(outcomes) / len(outcomes),
            }
        )

    betting = None
    if simulate_betting and min_edge is not None:
        peak = 0.0
        max_dd = 0.0
        for b in bankroll_curve:
            peak = max(peak, b)
            max_dd = max(max_dd, peak - b)

        betting = BettingResult(
            bets_placed=bets_placed,
            bets_won=bets_won,
            hit_rate=bets_won / bets_placed if bets_placed else 0.0,
            total_staked=total_staked,
            net_profit=net_profit,
            roi=net_profit / total_staked if total_staked else 0.0,
            max_drawdown=max_dd,
            min_edge_used=min_edge,
        )

    summary = {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "avg_log_loss": total_log_loss / total if total else 0.0,
        "avg_brier": total_brier / total if total else 0.0,
        "home_win_rate": home_win_rate,
        "baseline_accuracy": baseline_accuracy,
        "by_season": by_season,
        "calibration": calibration,
    }
    return summary, rows, betting


def run_backtest(
    mode: str = "live",
    *,
    min_edge: float = 0.03,
    simulate_betting: bool = True,
    export_csv: bool = True,
) -> BacktestResult:
    """
    Modos:
    - live: predice y actualiza Elo en orden cronológico (simula uso real).
    - walk_forward: entrena temporadas pasadas, evalúa la siguiente sin mezclar futuro.
    """
    init_db()
    with get_connection() as conn:
        all_games = fetch_final_games(conn)

    if not all_games:
        raise RuntimeError("No hay partidos en la base de datos. Ejecuta: python main.py fetch")

    all_rows: list[dict] = []

    if mode == "live":
        model = EloModel()
        summary, rows, betting = _evaluate_games(
            all_games,
            model,
            update_after=True,
            min_edge=min_edge,
            simulate_betting=simulate_betting,
        )
        all_rows = rows

    elif mode == "walk_forward":
        seasons = sorted({int(g["season"]) for g in all_games})
        if len(seasons) < 2:
            raise RuntimeError("Se necesitan al menos 2 temporadas para walk-forward.")

        combined = {
            "total": 0,
            "correct": 0,
            "avg_log_loss": 0.0,
            "avg_brier": 0.0,
            "home_wins": 0,
            "by_season": {},
        }
        total_bets = total_won = 0
        total_staked = total_profit = 0.0
        max_dd = 0.0
        bankroll = 0.0
        peak = 0.0

        for test_season in seasons[1:]:
            train = [g for g in all_games if int(g["season"]) < test_season]
            test = [g for g in all_games if int(g["season"]) == test_season]

            model = EloModel()
            for g in train:
                model.update(g["home_team_id"], g["away_team_id"], int(g["home_win"]))

            summary, rows, betting = _evaluate_games(
                test,
                model,
                update_after=False,
                min_edge=min_edge,
                simulate_betting=simulate_betting,
            )
            all_rows.extend(rows)

            combined["total"] += summary["total"]
            combined["correct"] += summary["correct"]
            combined["avg_log_loss"] += summary["avg_log_loss"] * summary["total"]
            combined["avg_brier"] += summary["avg_brier"] * summary["total"]
            combined["home_wins"] += int(summary["home_win_rate"] * summary["total"])
            combined["by_season"][test_season] = summary["by_season"][test_season]

            if betting:
                total_bets += betting.bets_placed
                total_won += betting.bets_won
                total_staked += betting.total_staked
                total_profit += betting.net_profit
                bankroll += betting.net_profit
                peak = max(peak, bankroll)
                max_dd = max(max_dd, peak - bankroll)

        total = combined["total"]
        home_win_rate = combined["home_wins"] / total if total else 0.0
        summary = {
            "total": total,
            "correct": combined["correct"],
            "accuracy": combined["correct"] / total if total else 0.0,
            "avg_log_loss": combined["avg_log_loss"] / total if total else 0.0,
            "avg_brier": combined["avg_brier"] / total if total else 0.0,
            "home_win_rate": home_win_rate,
            "baseline_accuracy": max(home_win_rate, 1 - home_win_rate),
            "by_season": combined["by_season"],
            "calibration": [],
        }
        betting = None
        if simulate_betting:
            betting = BettingResult(
                bets_placed=total_bets,
                bets_won=total_won,
                hit_rate=total_won / total_bets if total_bets else 0.0,
                total_staked=total_staked,
                net_profit=total_profit,
                roi=total_profit / total_staked if total_staked else 0.0,
                max_drawdown=max_dd,
                min_edge_used=min_edge,
            )

    else:
        raise ValueError(f"Modo desconocido: {mode}")

    if export_csv and all_rows:
        _export_predictions(all_rows, mode)

    # Calibración desde filas exportadas (live y walk-forward)
    cal_buckets: dict[str, list[int]] = defaultdict(list)
    for row in all_rows:
        prob = row["home_win_prob"]
        bucket = f"{int(prob * 10) * 10}-{int(prob * 10) * 10 + 10}%"
        cal_buckets[bucket].append(int(row["home_win"]))
    calibration = [
        {
            "bucket": label,
            "games": len(outcomes),
            "actual_home_win_rate": sum(outcomes) / len(outcomes),
        }
        for label, outcomes in sorted(cal_buckets.items())
    ]

    return BacktestResult(
        mode=mode,
        total_games=summary["total"],
        correct=summary["correct"],
        accuracy=summary["accuracy"],
        avg_log_loss=summary["avg_log_loss"],
        avg_brier=summary["avg_brier"],
        home_win_rate=summary["home_win_rate"],
        baseline_accuracy=summary["baseline_accuracy"],
        by_season=summary["by_season"],
        betting=betting,
        calibration=calibration,
    )


def _export_predictions(rows: list[dict], mode: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"backtest_{mode}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def print_backtest_report(result: BacktestResult) -> None:
    mode_label = "Live (cronológico)" if result.mode == "live" else "Walk-forward (OOS)"
    print(f"\n=== BACKTEST MLB — {mode_label} ===")
    print(f"Partidos evaluados:  {result.total_games}")
    print(f"Aciertos:            {result.correct} ({result.accuracy:.1%})")
    print(f"Baseline (mayoría):  {result.baseline_accuracy:.1%}")
    print(f"Ventaja vs baseline: {result.accuracy - result.baseline_accuracy:+.1%}")
    print(f"Log loss promedio:   {result.avg_log_loss:.4f}  (menor = mejor)")
    print(f"Brier score:         {result.avg_brier:.4f}  (menor = mejor)")
    print(f"% victorias local:   {result.home_win_rate:.1%}")
    print(f"Elo inicial:         {INITIAL_ELO}")

    print("\n--- Por temporada ---")
    for season, s in result.by_season.items():
        print(
            f"  {season}: {int(s['games'])} juegos | "
            f"accuracy {s['accuracy']:.1%} | log loss {s['avg_log_loss']:.4f}"
        )

    if result.betting and result.betting.bets_placed > 0:
        b = result.betting
        print("\n--- Simulación de apuestas (cuotas simuladas -110) ---")
        print(f"Edge mínimo:         {b.min_edge_used:.1%}")
        print(f"Apuestas:            {b.bets_placed}")
        print(f"Ganadas:             {b.bets_won} ({b.hit_rate:.1%})")
        print(f"Unidades apostadas:  {b.total_staked:.0f}")
        print(f"Beneficio neto:      {b.net_profit:+.2f} u")
        print(f"ROI:                 {b.roi:+.1%}")
        print(f"Drawdown máximo:     {b.max_drawdown:.2f} u")
        print("  (Sin cuotas reales aún — preparado para API de odds)")
    elif result.betting:
        print("\n--- Simulación de apuestas ---")
        print(f"  Sin apuestas con edge >= {result.betting.min_edge_used:.1%}")

    if result.calibration:
        print("\n--- Calibracion (predicho vs real) ---")
        for c in result.calibration:
            if c["games"] >= 50:
                print(
                    f"  {c['bucket']:>8}  n={int(c['games']):4d}  "
                    f"real local gana {c['actual_home_win_rate']:.1%}"
                )

    csv_name = f"backtest_{result.mode}.csv"
    print(f"\nDetalle exportado: data/{csv_name}")
