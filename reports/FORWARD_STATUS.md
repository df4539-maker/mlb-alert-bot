# Forward test — estado

## Filtro oficial (FIJO)

- Solo cuenta / solo apostar: **P modelo >= 50% (CON)** y **edge >= +3%** vs cuota real.
- CONTRA o CON sin value: fuera de protocolo.
- Meta **250** ops oficiales.

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

**Oficial:** 6W / 3L · stake L175 · neto **+43.15** · ROI **+24.7%** · contador **9 / 250**

Baseline: win 55.9% · ROI +6.7%.

## Card 2026-08-06

| # | Partido | Apostá | Lado | P | Cuota modelo | Edge | Stake sug. |
|---|---------|--------|------|---|--------------|------|------------|
| 1 | ATH @ CIN | **CIN** | **1** | 66.6% | 1.50 | +14.2% | L20 |
| 2 | LAA @ BAL | **BAL** | **1** | 64.8% | 1.54 | +12.4% | L20 |
| 3 | CWS @ BOS | **BOS** | **1** | 62.1% | 1.61 | +9.8% | L20 |
| 4 | DET @ SEA | **DET** | **2** | 60.3% | 1.66 | +7.9% | L15 |
| 5 | MIN @ KC | **MIN** | **2** | 58.8% | 1.70 | +6.4% | L15 |
| 6 | PIT @ MIL | **MIL** | **1** | 57.9% | 1.73 | +5.5% | L15 |
| 7 | TOR @ CHC | **CHC** | **1** | 57.2% | 1.75 | +4.8% | L15 |
| 8 | MIA @ ATL | **ATL** | **1** | 56.1% | 1.78 | +3.8% | L15 |
| 9 | NYM @ CLE | **NYM** | **2** | 55.6% | 1.80 | +3.2% | L15 |

Verificar cuota Hondubet: si edge real < 3%, saltar. Prioridad bank chico: 1-5.

CSV: `data/forward_bets.csv` · Rutina: `reports/RUTINA.md`
