# Forward test — estado

## Filtro oficial (FIJO)

- **CON** (P >= 50%). CONTRA: nunca.
- **Mañana (entrada temprana):** edge **>= +5%**.
- **Resto del día / contador 250:** edge **>= +3%**.
- **Preferencia usuario:** priorizar **edge >= +10%** en el card (seguir listando el resto del filtro oficial).
- Meta **250** ops = CON + edge>=3%.

## Oficiales cerradas (CON + edge>=3%)

| # | Fecha | Partido | Lado | Cuota | Stake | P | Edge | Resultado | Profit |
|---|-------|---------|------|-------|-------|---|------|-----------|--------|
| 1 | 2026-08-02 | BOS @ LAD | BOS(2) | 2.55 | L25 | 60.7% | +21.5% | GANÓ | +38.75 |
| 2 | 2026-08-04 | LAA @ BAL | BAL(1) | 1.76 | L10 | 60.7% | +3.9% | GANÓ | +7.60 |
| 3 | 2026-08-05 | CWS @ BOS | BOS(1) | 1.76 | L20 | 59.9% | +3.1% | GANÓ | +15.20 |
| 4 | 2026-08-05 | MIN @ KC | MIN(2) | 2.05 | L20 | 62.2% | +13.4% | PERDIÓ | -20.00 |
| 5 | 2026-08-05 | TB @ COL | TB(2) | 1.62 | L20 | 70.9% | +9.2% | GANÓ | +12.40 |
| 6 | 2026-08-05 | LAA @ BAL | BAL(1) | 1.80 | L20 | 62.8% | +7.3% | GANÓ | +16.00 |
| 7 | 2026-08-05 | DET @ SEA | DET(2) | 2.25 | L20 | 61.7% | +17.2% | PERDIÓ | -20.00 |
| 8 | 2026-08-05 | ATH @ CIN | CIN(1) | 1.66 | L20 | 64.8% | +4.5% | GANÓ | +13.20 |
| 9 | 2026-08-05 | LAD @ CHC | LAD(2) | 2.10 | L20 | 52.8% | +5.2% | PERDIÓ | -20.00 |

**Oficial cerrado:** 13W / 7L · stake L430 · neto **+104.25** · ROI **+24.2%** · hit **65.0%** · contador **20 / 250**

Baseline backtest: win 55.9% · ROI +6.7%. Muestra chica.

## Card 2026-08-06 — cerrado
DET/MIN ambas W. Ver CSV.

## Card 2026-08-07 — CERRADO
3W/3L · L120 · neto ≈ −20.97. Preferidas ≥10%: 2W/2L ≈ −8.24. Ver CSV.
Oficial tras el día: **15/250** · 9W/6L · ROI +15.2% · neto +46.38.

## Card 2026-08-08 — CERRADO
TB@SEA **2 TB** @2.00 L25 ticket 5276132784 → **GANÓ** (+25) score 3:2. Preferida +18.5%.
Oficial tras el día: **16/250** · 10W/6L · ROI +21.6% · neto +71.38.

## Card 2026-08-09 — CERRADO
3W/1L · L100 · neto **+32.87**. Preferidas ≥10%: BOS L / DET W / TB W. CHC W edge +9.5%.
Oficial tras el día: **20/250** · 13W/7L · ROI +24.2% · neto +104.25.
Tanking: `tanking_baseline.html` · canvas `mlb-baseline-cuadro`.

CSV: data/forward_bets.csv · Rutina: reports/RUTINA.md

