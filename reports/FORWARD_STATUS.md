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

**Oficial cerrado:** 10W / 6L · stake L330 · neto **+71.38** · ROI **+21.6%** · hit **62.5%** · contador **16 / 250**

Baseline backtest: win 55.9% · ROI +6.7%. Muestra chica.

## Card 2026-08-06 — cerrado
DET/MIN ambas W. Ver CSV.

## Card 2026-08-07 — CERRADO
3W/3L · L120 · neto ≈ −20.97. Preferidas ≥10%: 2W/2L ≈ −8.24. Ver CSV.
Oficial tras el día: **15/250** · 9W/6L · ROI +15.2% · neto +46.38.

## Card 2026-08-08 — CERRADO
TB@SEA **2 TB** @2.00 L25 ticket 5276132784 → **GANÓ** (+25) score 3:2. Preferida +18.5%.
Oficial tras el día: **16/250** · 10W/6L · ROI +21.6% · neto +71.38.

## Card 2026-08-09 — mañana ~09:40 HN (PC bots)

**Preferencia:** edge ≥ +10%. Filtro mañana ≥ +5% · día/contador ≥ +3%. 1=local 2=visita.

### Preferidas (≥ +10%) — priorizar
| # | Partido | Apuesta | P | Cuota mod | Edge | Hora HN | Stake |
|---|---------|---------|---|-----------|------|---------|-------|
| 1 | ATH @ BOS | **1 BOS** | 82.6% | 1.21 | +30.2% | 14:10 | L20 |
| 2 | CHC @ KC | **2 CHC** | 75.3% | 1.33 | +22.9% | 17:10 | L20 |
| 3 | TB @ SEA | **2 TB** | 68.5% | 1.46 | +16.1% | 19:50 | L20 |
| 4 | DET @ SF | **2 DET** | 65.1% | 1.54 | +12.7% | 17:15 | L20 |

### Listadas +5–10% — no apostar (preferencia &lt;10%)
| # | Partido | Apuesta | P | Edge | Hora HN |
|---|---------|---------|---|------|---------|
| 5 | CIN @ WSH | **2 CIN** | 62.1% | +9.7% | 16:45 |
| 6 | HOU @ SD | **2 HOU** | 61.9% | +9.5% | 17:15 |
| 7 | ATL @ NYY | **2 ATL** | 59.9% | +7.5% | 13:05 |
| 8 | NYM @ PIT | **2 NYM** | 59.3% | +6.9% | 16:40 |

### Cola día +3–5% — no apostar (&lt;10%)
MIN@MIL **1 MIL** +3.4% · BAL@TEX **2 BAL** +3.2%

### Fuera de protocolo
LAA@MIA · TOR@PHI · COL@STL · CLE@CWS · LAD@AZ

### Reglas (pie)
1. Solo CON (P>=50%). Nunca CONTRA.
2. Manana: edge>=5%. Resto del dia / contador 250: edge>=3%.
3. Preferencia: apostar solo si edge real >=+10%; listar el resto.
4. edge = P − 1/cuota_real Hondubet. Si acorta -> skip.
5. Solo PRE-MATCH. Stake 1-2% bank. Oficial 16/250.

CSV: data/forward_bets.csv · Rutina: reports/RUTINA.md

