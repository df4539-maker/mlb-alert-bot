"""Evaluacion estadistica de la estrategia (LLN, tamano muestral, prueba de hipotesis)."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from mlb.betting import DEFAULT_DECIMAL_ODDS, decimal_to_implied_prob
from mlb.config import DATA_DIR

# Z criticos aproximados (normal estandar)
Z_95 = 1.96
Z_90 = 1.645
Z_80_POWER = 0.84  # potencia ~80%
Z_90_POWER = 1.28  # potencia ~90%


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def break_even_win_rate(decimal_odds: float = DEFAULT_DECIMAL_ODDS) -> float:
    """Win rate necesario para ROI = 0 con cuota plana."""
    return decimal_to_implied_prob(decimal_odds)


@dataclass
class SampleSizePlan:
    break_even: float
    target_win_rate: float
    alpha: float
    power: float
    n_required: int
    bankroll_units: float
    stake_units: float
    max_bets_affordable: int
    verdict: str


@dataclass
class HypothesisResult:
    n: int
    wins: int
    hit_rate: float
    break_even: float
    edge_vs_break_even: float
    net_profit_units: float
    roi: float
    # H0: hit_rate <= break_even (no hay ventaja)
    z_stat: float
    p_value: float
    reject_h0_95: bool
    ci95_low: float
    ci95_high: float
    se: float
    lln_note: str
    verdict: str


def required_sample_size(
    p0: float,
    p1: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    n para test unilateral H0: p <= p0 vs H1: p = p1.
    Usa formula clasica de proporciones (aprox. normal).
    """
    if p1 <= p0:
        raise ValueError("p1 (win rate objetivo) debe ser mayor que p0 (break-even)")
    z_a = Z_95 if abs(alpha - 0.05) < 1e-9 else Z_90
    z_b = Z_80_POWER if abs(power - 0.80) < 1e-9 else Z_90_POWER
    numer = z_a * math.sqrt(p0 * (1.0 - p0)) + z_b * math.sqrt(p1 * (1.0 - p1))
    n = (numer / (p1 - p0)) ** 2
    return max(1, int(math.ceil(n)))


def plan_forward_test(
    *,
    bankroll: float = 500.0,
    stake: float = 5.0,
    decimal_odds: float = DEFAULT_DECIMAL_ODDS,
    assumed_edge: float = 0.03,
    alpha: float = 0.05,
    power: float = 0.80,
) -> SampleSizePlan:
    """
    Planifica cuantas apuestas L5 necesitas para detectar un edge
    (ley de grandes numeros + potencia estadistica).
    """
    p0 = break_even_win_rate(decimal_odds)
    p1 = min(p0 + assumed_edge, 0.99)
    n = required_sample_size(p0, p1, alpha=alpha, power=power)
    max_bets = int(bankroll // stake) if stake > 0 else 0

    if max_bets >= n:
        verdict = (
            f"Con bankroll {bankroll:.0f} y stake {stake:.0f} alcanzan ~{max_bets} tiros; "
            f"el n minimo teorico es {n}. Puedes completar la muestra."
        )
    else:
        verdict = (
            f"Teoricamente necesitas ~{n} apuestas para detectar edge {assumed_edge:.0%} "
            f"con potencia {power:.0%}, pero solo caben ~{max_bets} tiros de {stake:.0f}. "
            f"Con {max_bets} pruebas puedes EXPLORAR, no DEMOSTRAR con confianza alta. "
            f"Aun asi sirve como forward test exploratorio."
        )

    return SampleSizePlan(
        break_even=p0,
        target_win_rate=p1,
        alpha=alpha,
        power=power,
        n_required=n,
        bankroll_units=bankroll,
        stake_units=stake,
        max_bets_affordable=max_bets,
        verdict=verdict,
    )


def evaluate_bets(
    outcomes: list[bool],
    profits: list[float],
    *,
    decimal_odds: float = DEFAULT_DECIMAL_ODDS,
) -> HypothesisResult:
    """
    Prueba H0: no hay edge (hit rate <= break-even en -110).
    H1: hit rate > break-even.
    """
    n = len(outcomes)
    if n == 0:
        raise ValueError("No hay apuestas para evaluar")

    wins = sum(1 for o in outcomes if o)
    hit = wins / n
    p0 = break_even_win_rate(decimal_odds)
    se = math.sqrt(p0 * (1.0 - p0) / n)
    z = (hit - p0) / se if se > 0 else 0.0
    # unilateral (cola derecha)
    p_value = 1.0 - norm_cdf(z)

    # IC 95% para hit rate (Wald)
    se_hat = math.sqrt(hit * (1.0 - hit) / n) if 0 < hit < 1 else se
    ci_low = max(0.0, hit - Z_95 * se_hat)
    ci_high = min(1.0, hit + Z_95 * se_hat)

    net = sum(profits)
    roi = net / n if n else 0.0  # profit por unidad apostada (stake=1 en backtest)

    if n < 30:
        lln = (
            f"n={n} es pequeno: la ley de grandes numeros aun no estabiliza. "
            "Trata el resultado como exploratorio."
        )
    elif n < 100:
        lln = (
            f"n={n}: la media empieza a estabilizarse, pero el IC sigue ancho. "
            "Bueno para senal preliminar."
        )
    else:
        lln = (
            f"n={n}: muestra grande; el hit rate observado debería acercarse "
            "al valor verdadero de la estrategia (si el proceso no cambia)."
        )

    reject = p_value < 0.05 and hit > p0
    if reject:
        verdict = (
            "Se RECHAZA H0 al 5%: hay evidencia estadistica de hit rate "
            "por encima del break-even (estrategia con senal)."
        )
    elif hit > p0:
        verdict = (
            "Hit rate > break-even, pero NO significativo al 5% "
            "(podria ser azar). Sigue acumulando muestra."
        )
    else:
        verdict = (
            "No se rechaza H0: no hay evidencia de que la estrategia "
            "supere el break-even con estos datos."
        )

    return HypothesisResult(
        n=n,
        wins=wins,
        hit_rate=hit,
        break_even=p0,
        edge_vs_break_even=hit - p0,
        net_profit_units=net,
        roi=roi,
        z_stat=z,
        p_value=p_value,
        reject_h0_95=reject,
        ci95_low=ci_low,
        ci95_high=ci_high,
        se=se_hat,
        lln_note=lln,
        verdict=verdict,
    )


def load_backtest_bets(csv_path: Path) -> tuple[list[bool], list[float]]:
    outcomes: list[bool] = []
    profits: list[float] = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("bet_side"):
                continue
            won = str(row.get("bet_won", "")).strip()
            if won == "":
                continue
            outcomes.append(won in ("1", "True", "true"))
            profits.append(float(row.get("profit") or 0.0))
    return outcomes, profits


def load_forward_bets(csv_path: Path) -> tuple[list[bool], list[float]]:
    outcomes: list[bool] = []
    profits: list[float] = []
    if not csv_path.exists():
        return outcomes, profits
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = (row.get("result") or "").strip().lower()
            if result not in ("win", "loss", "won", "lost"):
                continue
            won = result in ("win", "won")
            outcomes.append(won)
            stake = float(row.get("stake") or 0.0)
            odds = float(row.get("decimal_odds") or DEFAULT_DECIMAL_ODDS)
            if won:
                profits.append(stake * (odds - 1.0))
            else:
                profits.append(-stake)
    return outcomes, profits


def print_plan(plan: SampleSizePlan) -> None:
    print("\n=== PLAN MUESTRAL (Ley de grandes numeros + potencia) ===")
    print(f"Break-even (-110):     {plan.break_even:.2%}")
    print(f"Win rate objetivo:     {plan.target_win_rate:.2%}  (edge asumido)")
    print(f"Alpha (falso positivo):{plan.alpha:.0%}")
    print(f"Potencia deseada:      {plan.power:.0%}")
    print(f"n minimo teorico:      {plan.n_required} apuestas")
    print(f"Bankroll / stake:      {plan.bankroll_units:.0f} / {plan.stake_units:.0f}")
    print(f"Tiros posibles:        {plan.max_bets_affordable}")
    print(f"\n{plan.verdict}")


def print_hypothesis(result: HypothesisResult, title: str) -> None:
    print(f"\n=== PRUEBA DE HIPOTESIS — {title} ===")
    print("H0: hit rate <= break-even (no hay ventaja)")
    print("H1: hit rate > break-even (hay ventaja)")
    print(f"n apuestas:            {result.n}")
    print(f"Ganadas:               {result.wins} ({result.hit_rate:.2%})")
    print(f"Break-even:            {result.break_even:.2%}")
    print(f"Edge vs break-even:    {result.edge_vs_break_even:+.2%}")
    print(f"Profit neto (u):       {result.net_profit_units:+.2f}")
    print(f"ROI (por u apostada):  {result.roi:+.2%}")
    print(f"IC 95% hit rate:       [{result.ci95_low:.2%}, {result.ci95_high:.2%}]")
    print(f"z:                     {result.z_stat:.3f}")
    print(f"p-value (unilateral):  {result.p_value:.4f}")
    print(f"Rechaza H0 (5%):       {'SI' if result.reject_h0_95 else 'NO'}")
    print(f"\nLLN: {result.lln_note}")
    print(f"\nVeredicto: {result.verdict}")


def run_evaluation(
    *,
    bankroll: float = 500.0,
    stake: float = 5.0,
    assumed_edge: float = 0.03,
    backtest_mode: str = "live",
) -> None:
    plan = plan_forward_test(
        bankroll=bankroll,
        stake=stake,
        assumed_edge=assumed_edge,
    )
    print_plan(plan)

    bt_path = DATA_DIR / f"backtest_{backtest_mode}.csv"
    if bt_path.exists():
        outcomes, profits = load_backtest_bets(bt_path)
        if outcomes:
            result = evaluate_bets(outcomes, profits)
            print_hypothesis(result, f"Backtest {backtest_mode} (cuotas simuladas -110)")
        else:
            print(f"\nNo hay apuestas en {bt_path.name}. Corre: python main.py backtest")
    else:
        print(f"\nFalta {bt_path}. Corre: python main.py backtest --mode {backtest_mode}")

    fwd_path = DATA_DIR / "forward_bets.csv"
    outcomes_f, profits_f = load_forward_bets(fwd_path)
    if outcomes_f:
        result_f = evaluate_bets(outcomes_f, profits_f)
        print_hypothesis(result_f, "Forward test Hondubet (apuestas reales)")
    else:
        print(
            "\n--- Forward test ---\n"
            "Aun no hay resultados en data/forward_bets.csv.\n"
            "Registra cada L5 con: python main.py log-bet ..."
        )
