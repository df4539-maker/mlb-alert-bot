"""Utilidades de cuotas y simulación de apuestas (preparado para API de odds real)."""

from __future__ import annotations

# Cuota americana -110 ≈ 1.909 decimal; implica ~52.38% por lado (con vig)
DEFAULT_AMERICAN_ODDS = -110
DEFAULT_DECIMAL_ODDS = 1.909
DEFAULT_VIG = 0.045  # ~4.5% margen casa


def american_to_decimal(american: int | float) -> float:
    if american >= 100:
        return 1.0 + american / 100.0
    return 1.0 + 100.0 / abs(american)


def decimal_to_implied_prob(decimal_odds: float) -> float:
    return 1.0 / decimal_odds


def implied_prob_to_decimal(prob: float) -> float:
    if prob <= 0:
        raise ValueError("prob must be positive")
    return 1.0 / prob


def apply_vig(fair_prob: float, vig: float = DEFAULT_VIG) -> float:
    """Infla probabilidad justa para simular margen de la casa."""
    return min(fair_prob * (1.0 + vig), 0.99)


def market_odds_from_prob(prob: float, vig: float = DEFAULT_VIG) -> float:
    """Probabilidad implícita que mostraría una casa con margen."""
    return apply_vig(prob, vig)


def has_value(model_prob: float, market_implied_prob: float, min_edge: float) -> bool:
    """True si el modelo ve más valor que el mínimo exigido."""
    return model_prob - market_implied_prob >= min_edge


def bet_payout(stake: float, won: bool, decimal_odds: float = DEFAULT_DECIMAL_ODDS) -> float:
    """Retorno neto de una apuesta (positivo = ganancia, negativo = pérdida)."""
    if won:
        return stake * (decimal_odds - 1.0)
    return -stake
