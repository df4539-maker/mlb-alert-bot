# Forward test — estado

## Filtro oficial (FIJO)

- **CON** (P >= 50%). CONTRA: nunca.
- **Mañana (entrada temprana):** edge **>= +5%**.
- **Resto del día / contador 250:** edge **>= +3%**.
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

**Oficial:** 6W / 3L · stake L175 · neto **+43.15** · ROI **+24.7%** · contador **9 / 250**

Baseline: win 55.9% · ROI +6.7%.

## Card 2026-08-06 — estado tarde (PC bots)

### Apostadas hoy (protocolo OK)
| Partido | Lado | Cuota | Stake | P | Edge real | Ticket | Estado |
|---------|------|-------|-------|---|-----------|--------|--------|
| DET @ SEA | DET (2) | 2.05 | L25 | 60.3% | +11.5% | 5267976850 | ABIERTO |
| MIN @ KC | MIN (2) | 2.05 | L25 | 58.8% | +10.0% | 5268045979 | ABIERTO |

### No apostadas (motivo)
| Partido | Motivo |
|---------|--------|
| CIN / BAL / NYM / MIL / CHC | Ya iniciados o warmup al mediodía |
| CWS @ BOS @1.54 | Edge real -2.8% (cara) |
| MIA @ ATL @1.66 | Edge real -4.1% (cara) |
| WSH @ PHI / SD @ AZ | Edge < 3% o negativo |

### Posibles tarde (solo si mejora cuota)
- BOS local: necesita ~1.69+ (edge>=3%)
- ATL local: necesita ~1.88+ (edge>=3%)

### Reglas (pie)
1. Solo CON (P>=50%). Nunca CONTRA.
2. Manana: edge>=5%. Resto del dia / contador 250: edge>=3%.
3. Si cuota Hondubet baja el umbral -> saltar.
4. Solo PRE-MATCH.
5. Stake 1-2% bank.
6. Noche: cerrar DET/MIN y comparar vs card.

Oficial cerrado previo: 9/250 · 6W/3L · +43.15
CSV: data/forward_bets.csv · Rutina: reports/RUTINA.md

