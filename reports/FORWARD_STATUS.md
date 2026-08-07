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

**Oficial:** 6W / 3L · stake L175 · neto **+43.15** · ROI **+24.7%** · contador **9 / 250**

Baseline: win 55.9% · ROI +6.7%.

## Card 2026-08-06 — cerrado
DET/MIN ambas W. Ver CSV.

## Card 2026-08-07 — estado tarde (PC bots)

**Preferencia:** edge ≥ +10% (filtro oficial sigue ≥3%).

### Apostadas hoy (ABIERTO)
| Partido | Lado | Cuota | Stake | P | Edge real | Ticket | Preferida |
|---------|------|-------|-------|---|-----------|--------|-----------|
| ATH @ BOS | BOS (1) | 1.36 | L20 | 82.0% | +8.5% | 5271192570 | no (&lt;10%) |
| CHC @ KC | CHC (2) | 1.58 | L20 | 74.2% | +10.9% | 5271202617 | sí |
| DET @ SF | DET (2) | 1.76 | L20 | 68.6% | +11.8% | 5271207680 | sí |
| TB @ SEA | TB (2) | 2.00 | L20 | 66.9% | +16.9% | 5271213441 | sí |
| CIN @ WSH | CIN (2) | 2.00 | L20 | 65.6% | +15.6% | 5271222953 | sí |
| ATL @ NYY | ATL (2) | 1.74 | L20 | 63.3% | +5.8% | 5271228155 | no (&lt;10%) |

Hoy: L120 · 6 tickets · 4 preferidas ≥10% + 2 ya puestas &lt;10%.

### No se apuestan (edge &lt; +10%)
| Partido | Lado card | Edge mod* | Motivo |
|---------|-----------|-----------|--------|
| HOU @ SD | HOU (2) | +7.3% | abajo de 10% — no apostar |
| MIN @ MIL | MIL (1) | +6.7% | abajo de 10% — no apostar |
| BAL @ TEX | BAL (2) | +6.5% | abajo de 10% — no apostar |
| NYM @ PIT | NYM (2) | +4.5% | abajo de 10% — no apostar |
| LAA @ MIA | MIA (1) | +4.2% | abajo de 10% — no apostar |

\*vs ref -110. Fuera de protocolo (&lt;3%): TOR@PHI, CLE@CWS, COL@STL, LAD@AZ.

### Reglas (pie)
1. Solo CON (P>=50%). Nunca CONTRA.
2. Manana: edge>=5%. Resto del dia / contador 250: edge>=3%.
3. Preferencia usuario: priorizar edge>=+10%; el resto listar pero no apostar si &lt;10%.
4. Si cuota Hondubet baja el umbral -> saltar.
5. Solo PRE-MATCH. Stake 1-2% bank.

CSV: data/forward_bets.csv · Rutina: reports/RUTINA.md

