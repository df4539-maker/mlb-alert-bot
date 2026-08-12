# Forward test — estado

## Filtro oficial (FIJO)

- **CON** (P >= 50%). CONTRA: nunca.
- **Mañana (entrada temprana):** edge **>= +5%**.
- **Resto del día / contador 250:** edge **>= +3%**.
- **Preferencia usuario:** priorizar **edge >= +10%** en el card (seguir listando el resto del filtro oficial).
- Meta **250** ops = CON + edge>=3%.
- Validación: checkpoint **30** · intermedia **~100** · decisión **250**. Hasta 30 sin cambiar método.

## Oficiales cerradas (CON + edge>=3%)

**Oficial cerrado:** 16W / 8L · stake L530 · neto **+131.87** · ROI **+24.9%** · hit **66.7%** · contador **24 / 250**

| Bucket | n | Record | Hit | ROI | Neto | Stake |
|--------|---|--------|-----|-----|------|-------|
| Baseline backtest | — | — | 55.9% | +6.7% | — | — |
| Todas | 36 | 22W/14L | 61.1% | +14.8% | +107.78 | L730 |
| Solo CON | 34 | 21W/13L | 61.8% | +17.5% | +122.28 | L700 |
| CON+edge≥3% (oficial) | 24 | 16W/8L | 66.7% | +24.9% | +131.87 | L530 |
| Preferida ≥10% | 15 | 10W/5L | 66.7% | +35.4% | +122.18 | L345 |

Muestra chica. Checkpoint: **24 → 30** (faltan **6**).

## Card 2026-08-10 — CERRADO

4W/1L · L125 · neto **+41.51**. Preferidas ≥10%: TEX W / TB W. Oficiales &lt;10%: BOS L / HOU W. AZ @1.55 edge real **−1.2%** (fuera protocolo; W no cuenta).

Oficial tras el día: **24/250** · 16W/8L · ROI +24.9% · neto +131.87.
Tanking: `tanking_baseline.html` · canvas `mlb-baseline-cuadro` · calendario `calendario_mensual.html`.

## Card 2026-08-11 — mañana (PC bots) bank ~L1543 · L25

**Preferencia:** edge ≥ +10% (filtro mañana ≥5%; resto del día ≥3%).

### Apostadas hoy

| Hora HN | Partido | Lado | Cuota | Edge real | Stake | Ticket | Estado | Nota |
|---------|---------|------|-------|-----------|-------|--------|--------|------|
| 16:45 | CHC @ WSH | CHC (2) | 1.58 | +5.6% | L25 | 5283364050 | **ABIERTO** | oficial ≥5%; no prefer |
| 17:07 | BOS @ TOR | BOS (2) | 2.30 | +24.7% | L25 | 5283366437 | **ABIERTO** | PREF ≥10% |
| 17:45 | PHI @ STL | PHI (2) | 1.58 | +0.0% | L25 | 5283369262 | CERRADO −2.79 | FUERA cashout |
| 19:38 | TEX @ LAA | TEX (2) | 1.71 | +12.5% | L25 | 5283372113 | **ABIERTO** | PREF ≥10% |
| 19:40 | COL @ AZ | AZ (1) | 1.55 | +0.7% | L25 | 5283375743 | CERRADO −2.79 | FUERA cashout |
| 19:40 | TB @ ATH | TB (2) | 1.60 | +18.0% | L25 | 5283377337 | **ABIERTO** | PREF ≥10% |
| 19:40 | TB @ ATH | TB (2) | 1.52 | +14.7% | L25 | 5285552204 | **ABIERTO** | PREF ≥10% · **2º ticket mismo partido 11 ago** |
| 19:45 | HOU @ SF | HOU (2) | 1.52 | +4.9% | L25 | 5283379280 | **ABIERTO** | oficial ≥3%; bajo mañana 5% |

**Abiertas (método) 11 ago:** L150 · incluye **2× TB@ATH** (L50 mismo juego).  
**Fuera cerradas hoy:** PHI −2.79 + AZ −2.79 = **−5.58** (no cuentan a oficial). Oficial sigue **24/250**.

### Seguimiento ABIERTAS — 2026-08-11 (L150 · 6 tickets; TB×2)

| Fecha | HN | Partido | Lado | Cuota | Edge real | Stake | Ticket | Nota |
|-------|----|---------|------|-------|-----------|-------|--------|------|
| 2026-08-11 | 16:45 | CHC@WSH | 2 CHC | 1.58 | +5.6% | L25 | 5283364050 | oficial |
| 2026-08-11 | 17:07 | BOS@TOR | 2 BOS | 2.30 | +24.7% | L25 | 5283366437 | PREF |
| 2026-08-11 | 19:38 | TEX@LAA | 2 TEX | 1.71 | +12.5% | L25 | 5283372113 | PREF |
| 2026-08-11 | 19:40 | TB@ATH | 2 TB | 1.60 | +18.0% | L25 | 5283377337 | PREF |
| 2026-08-11 | 19:40 | TB@ATH | 2 TB | 1.52 | +14.7% | L25 | 5285552204 | PREF · 2º ticket |
| 2026-08-11 | 19:45 | HOU@SF | 2 HOU | 1.52 | +4.9% | L25 | 5283379280 | oficial &lt;5% |

Fuera cerradas hoy: PHI −2.79 + AZ −2.79 = −5.58. Oficial **24/250**.

### Card MAÑANA 2026-08-12 (HB cargado · sin abiertas · sin 13–14)

Rivales ya abiertos del 11 **quitados** (TB/HOU/CHC/BOS/TEX).

| Fecha | HN | Partido | Lado | P | Mod | Mín ≥5% | Mín ≥10% | Hondubet | Edge real | ¿Apostar? | Stake |
|-------|----|---------|------|---|-----|---------|----------|----------|-----------|-----------|-------|
| 2026-08-12 | 11:40 | BAL@MIN | 2 BAL | 55.9% | 1.79 | 1.97 | 2.18 | **2.00** | +5.9% | **SÍ ≥5% · no preferido (5–10%)** | L25 |
| 2026-08-12 | 12:15 | PHI@STL | 2 PHI | 63.3% | 1.58 | 1.72 | 1.88 | **1.62** | +1.5% | **NO — observar** | — |
| 2026-08-12 | 13:40 | COL@AZ | 1 AZ | 65.2% | 1.53 | 1.66 | 1.81 | **1.58** | +1.9% | **NO — observar** | — |
| 2026-08-12 | 14:10 | MIL@SD | 2 MIL | 58.7% | 1.70 | 1.86 | 2.05 | **1.80** | +3.1% | **NO — observar** | — |
| 2026-08-12 | 16:40 | CLE@DET | 1 DET | 55.8% | 1.79 | 1.97 | 2.18 | **1.76** | −1.0% | **NO — observar** | — |
| 2026-08-12 | 17:05 | SEA@NYY | 1 NYY | 56.2% | 1.78 | 1.95 | 2.17 | **1.80** | +0.6% | **NO — observar** | — |
| 2026-08-12 | 20:10 | KC@LAD | 1 LAD | 57.2% | 1.75 | 1.91 | 2.12 | **1.38** | −15.3% | **NO — no apostar** (muy bajo Mod) | — |

**Operable mañana:** solo BAL@MIN @2.00 (no preferido). Resto NO. Preferidas del 12 (PHI/AZ/etc.) con HB corta; rivales fuertes ya abiertos el 11.

**Pendiente HB (13–14):** no listar hasta que Hondubet cargue.

### PREFERIDAS (≥10% vs −110) — pendientes de cuota real

Ninguna pendiente del card de la mañana.

### Mid (5–10%) — listar / no priorizar

| Hora HN | Partido | Lado | P | Mod | Edge | Stake |
|---------|---------|------|---|-----|------|-------|
| 19:40 | MIL @ SD | MIL (2) | 58.7% | 1.70 | +6.3% | L25 |

### Day3 (3–5%) — solo si resto del día (≥3%); mañana no

| Hora HN | Partido | Lado | P | Edge |
|---------|---------|------|---|------|
| 16:40 | CLE @ DET | DET (1) | 55.8% | +3.4% |
| 17:05 | SEA @ NYY | NYY (1) | 56.2% | +3.8% |
| 17:40 | BAL @ MIN | BAL (2) | 55.9% | +3.5% |
| 20:10 | KC @ LAD | LAD (1) | 57.2% | +4.8% |

**Antes de apostar:** verificar cuota real Hondubet → `edge = P − 1/cuota`. Si real &lt;3%, saltar (lección AZ 10 ago).

### Reglas al pie (FIJAS)

- Solo CON (P≥50%). Nunca CONTRA. Solo PRE-MATCH.
- Mañana 6–8: edge ≥5%. Resto del día / contador 250: ≥3%.
- Preferencia bank chico: **≥10%**. Tope stake **L25** (~1.62% de L1543).
- Contador oficial = CON + edge≥3% → **24/250**.

CSV: data/forward_bets.csv · Rutina: reports/RUTINA.md
