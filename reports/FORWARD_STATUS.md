# Forward test — estado

## Cerradas (P modelo **as-of** fecha del partido)

| # | Fecha | Partido | Lado | Cuota | Stake | P modelo | Cuota modelo | Edge | Con/Contra | Resultado | Profit |
|---|-------|---------|------|-------|-------|----------|--------------|------|------------|-----------|--------|
| 1 | 2026-08-02 | BOS @ LAD | BOS(2) | 2.55 | L25 | 60.7% | 1.65 | +21.5% | con | GANÓ | +38.75 |
| 2 | 2026-08-03 | TB @ COL | COL(1) | 1.55 | L10 | 30.6% | 3.27 | -33.9% | contra | GANÓ | +5.50 |
| 3 | 2026-08-03 | PIT @ MIL | MIL(1) | 1.64 | L10 | 55.8% | 1.79 | -5.1% | con | PERDIÓ | -10.00 |
| 4 | 2026-08-03 | LAD @ CHC | LAD(2) | 1.80 | L10 | 56.0% | 1.79 | +0.4% | con | PERDIÓ | -10.00 |
| 5 | 2026-08-03 | STL @ NYY | NYY(1) | 1.45 | L10 | 57.2% | 1.75 | -11.8% | con | PERDIÓ | -10.00 |
| 6 | 2026-08-04 | ATH @ CIN | ATH(2) | 2.15 | L20 | 37.2% | 2.69 | -9.3% | contra | PERDIÓ | -20.00 |
| 7 | 2026-08-04 | LAA @ BAL | BAL(1) | 1.76 | L10 | 60.7% | 1.65 | +3.9% | con | GANÓ | +7.60 |
| 8 | 2026-08-04 | TOR @ HOU | HOU(1) | 1.80 | L10 | 57.3% | 1.75 | +1.7% | con | GANÓ | +8.00 |

**Resumen cerradas:** 4W / 4L · stake L105 · neto **+9.85** · hit 50%

Baseline backtest: win 55.9% · ROI +6.7% (cuotas simuladas -110).

Elo as-of: entrenado solo con partidos **anteriores** a `game_date` (sin leak del propio juego).

## Pendientes 2026-08-05 (tickets reales; basura BOS Telegram eliminada)

| Partido | Lado | Cuota | Stake | Ticket |
|---------|------|-------|-------|--------|
| STL @ NYY | NYY (1) | 1.640 | L20 | 5263943929 |
| CWS @ BOS | BOS (1) | 1.760 | L20 | 5263952588 |
| MIN @ KC | MIN (2) | 2.050 | L20 | 5263956670 |
| TOR @ HOU | HOU (1) | 1.520 | L25 | 5263963632 |
| TB @ COL | TB (2) | 1.620 | L20 | 5263975720 |
| LAA @ BAL | BAL (1) | 1.800 | L20 | 5263937350 |
| DET @ SEA | DET (2) | 2.250 | L20 | 5263989310 |
| ATH @ CIN | CIN (1) | 1.660 | L20 | 5264008204 |
| PIT @ MIL | MIL (1) | 1.740 | L20 | 5264011497 |
| LAD @ CHC | LAD (2) | 2.100 | L20 | 5264014555 |

Pendientes: **10** · Fuente: `data/forward_bets.csv`

Gráficos: `reports/backtest_analisis.png`, `reports/baseline_vs_real.png`

## Filtro operativo (acuerdo)

- **No contar / no recomendar** apuestas en **contra** del modelo (P < 50%).
- Decisión a **250** ops mirando sobre todo **con + value** (edge >= 3% vs cuota real).
- Ver rutina completa: `reports/RUTINA.md`.

### Solo con modelo (cerradas, sin #2 COL ni #6 ATH)

6 ops · 3W/3L · L75 · neto +24.35 · ROI +32.5% (muestra chica; no concluible vs baseline +6.7%).

