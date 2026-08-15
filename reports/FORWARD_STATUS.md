# Forward test — estado

## Filtro oficial (FIJO)

- **CON** (P >= 50%). CONTRA: nunca.
- **Mañana (entrada temprana):** edge **>= +5%**.
- **Resto del día / contador 250:** edge **>= +3%**.
- **Preferencia usuario:** priorizar **edge >= +10%** en el card (seguir listando el resto del filtro oficial).
- Meta **250** ops = CON + edge>=3%.
- Validación: checkpoint **30** · intermedia **~100** · decisión **250**. Hasta 30 sin cambiar método.

## Oficiales cerradas (CON + edge>=3%)

**Oficial cerrado:** 21W / 14L · stake L805 · neto **+78.69** · ROI **+9.8%** · hit **60.0%** · contador **35 / 250**

| Bucket | n | Record | Hit | ROI | Neto | Stake |
|--------|---|--------|-----|-----|------|-------|
| Baseline backtest | — | — | 55.9% | +6.7% | — | — |
| Todas | 49 | 27W/22L | 55.1% | +4.6% | +49.02 | L1055 |
| Solo CON | 47 | 26W/21L | 55.3% | +6.2% | +63.52 | L1025 |
| CON+edge≥3% (oficial) | 35 | 21W/14L | 60.0% | +9.8% | +78.69 | L805 |
| Preferida ≥10% | 23 | 13W/10L | 56.5% | +10.2% | +55.49 | L545 |
| Mid 3–10% | 12 | 8W/4L | 66.7% | +8.9% | +23.20 | L260 |

**Checkpoint 30 pasado.** Noche 13: TEX L / PHI W / MIL W. Equity oficial **+78.69** · ROI otra vez arriba del baseline. No cambiar método → mira ~100.
Pending: **6** (BOS@PIT · SD@CLE · MIA@CIN · TEX@ATH · MIL@LAD · KC@LAA). Tanking: `tanking_baseline.html` · canvas `mlb-baseline-cuadro` · calendario `calendario_mensual.html`.

## Card 2026-08-14 — tarde

Bank ~L1543 · tope L25 · exposición abierta **L150 (~9.7% bank)** — **tope del día**.

### Cerradas esta mañana (noche 13)
| Fecha | HN | Partido | Lado | Cuota | Edge | Stake | Ticket | Res |
|-------|----|---------|------|-------|------|-------|--------|-----|
| 2026-08-13 | 20:07 | TEX@LAA | 2 TEX | 1.66 | +10.8% | L25 | 5292314864 | **PERDIDO** −25 · score 7:0 |
| 2026-08-13 | 17:30 | PHI@MIN | 2 PHI | 1.95 | +8.6% | L25 | 5289050853 | **GANADO** +23.81 · PA EP score 1:7 |
| 2026-08-13 | 20:10 | MIL@LAD | 2 MIL | 2.20 | +17.0% | L25 | 5289072719 | **GANADO** +30.00 · score 4:5 |

Noche 13 neta oficial: **+28.81**.

### Abiertas (6 · L150)
| Fecha | HN | Partido | Lado | Cuota | Edge real | Stake | Ticket | Estado |
|-------|----|---------|------|-------|-----------|-------|--------|--------|
| 2026-08-14 | 16:10 | MIA@CIN | 2 MIA | 1.95 | +5.1% | L25 | 5292387663 | SÍ ≥5% · ABIERTO |
| 2026-08-14 | 16:40 | BOS@PIT | 2 BOS | 1.66 | +12.8% | L25 | 5292327431 | PREF · ABIERTO |
| 2026-08-14 | 17:10 | SD@CLE | 2 SD | 2.10 | +20.0% | L25 | 5292340939 | PREF · ABIERTO |
| 2026-08-14 | 19:38 | KC@LAA | 2 KC | 1.90 | +8.4% | L25 | 5294984430 | SÍ ≥5% · no prefer · ABIERTO |
| 2026-08-14 | 19:40 | TEX@ATH | 2 TEX | 1.95 | +21.4% | L25 | 5294970921 | PREF · PA |
| 2026-08-14 | 20:10 | MIL@LAD | 2 MIL | 2.50 | +22.5% | L25 | 5294977348 | PREF · PA |

### Disponibles (PREF primero) · solo HB cargado · HN ~19:35

**Abiertas: 6 · L150 (~10% bank) — tope.** No meter más hasta que cierre algo.  
**16 ago:** nada cargado en HB → no listar como operable.  
**PREF libres:** ninguna (bloqueadas por abiertas).

#### SÍ ≥5% · no preferido (15)
| Fecha | HN | Partido | Lado | P | Mod | Mín ≥5% | Mín ≥10% | Hondubet | Edge real | ¿Apostar? | Stake |
|-------|----|---------|------|---|-----|---------|----------|----------|-----------|-----------|-------|
| 2026-08-15 | 16:10 | BAL@TB | **1 TB** | 58.3% | 1.72 | 1.88 | 2.07 | — | vs −110 +5.9% | SÍ ≥5% si HB≥1.88 · **espera bank** · (2 BAL = CONTRA) | L25 |

#### Oficial ≥3% (15)
| Fecha | HN | Partido | Lado | P | Mod | Mín ≥5% | Mín ≥10% | Hondubet | Edge real | ¿Apostar? | Stake |
|-------|----|---------|------|---|-----|---------|----------|----------|-----------|-----------|-------|
| 2026-08-15 | 17:10 | SEA@HOU | 1 HOU | 57.0% | 1.75 | 1.92 | 2.13 | — | vs −110 +4.6% | oficial ≥3% · **espera bank** | L25 |

**Fuera (edge):** STL@CHC 15 @1.64 (+0.9%) · PHI@MIN 15 @1.66 (−0.3%).  
**Pendiente HB 15:** NYY@TOR 13:07 · 2 NYY · Mod 1.69 · Mín≥5% 1.85 · Mín≥10% 2.04.  
**Pendiente HB 16:** todo el slate (aún no carga).  
**Bloqueados pending:** TEX@ATH · MIL@LAD · BOS@PIT · SD@CLE · MIA@CIN · KC@LAA.

### Analizadas · NO ingresamos (y por qué)
| Fecha | HN | Partido | Lado | HB | Edge real | Motivo |
|-------|----|---------|------|-----|-----------|--------|
| 2026-08-14 | 12:20 | STL@CHC | 1 CHC | 1.60 | −0.6% | HB ≤ Mod (1.62) · edge negativo |
| 2026-08-14 | 17:15 | NYY@TOR | 2 NYY | 1.64 | −2.0% | HB ≤ Mod (1.69) · edge negativo |
| 2026-08-14 | 18:10 | SEA@HOU | 1 HOU | 1.76 | +0.2% | edge &lt;3% (casi = Mod 1.75) · **revalidar si cuota sube** |
| 2026-08-15 | 12:20 | STL@CHC | 1 CHC | 1.64 | +0.9% | edge &lt;3% · fuera |
| 2026-08-15 | 17:10 | PHI@MIN | 2 PHI | 1.66 | −0.3% | HB ≤ Mod · fuera |

### Bloqueadas por pending abierto (mismo rival)
| Partido | Motivo |
|---------|--------|
| TEX@ATH 15/16 | ticket TEX@ATH 14 abierto |
| MIL@LAD 15/16 | ticket MIL@LAD 14 abierto |
| KC@LAA 15/16 | ticket KC@LAA 14 abierto |
| BOS@PIT 15 | ticket BOS@PIT 14 abierto |
| SD@CLE 15 | ticket SD@CLE 14 abierto |
| MIA@CIN 15 | ticket MIA@CIN 14 abierto |

### Pendiente HB — 15 ago (cuando cargue; tras cerrar 14)
| Fecha | HN | Partido | Lado | P | Mod | Mín ≥5% | Mín ≥10% | Nota |
|-------|----|---------|------|---|-----|---------|----------|------|
| 2026-08-15 | 17:15 | MIL@LAD | 2 MIL | 62.5% | 1.60 | 1.74 | 1.90 | fuera (pending 14) |
| 2026-08-15 | 12:20 | STL@CHC | 1 CHC | 61.9% | 1.62 | 1.76 | 1.93 | fuera @1.64 edge +0.9% |
| 2026-08-15 | 19:38 | KC@LAA | 2 KC | 61.0% | 1.64 | 1.79 | 1.96 | fuera (pending 14) |
| 2026-08-15 | 13:07 | NYY@TOR | 2 NYY | 59.0% | 1.69 | 1.85 | 2.04 | validar HB |
| 2026-08-15 | 16:10 | BAL@TB | 1 TB | 58.3% | 1.72 | 1.88 | 2.07 | validar HB |
| 2026-08-15 | 17:10 | SEA@HOU | 1 HOU | 57.0% | 1.75 | 1.92 | 2.13 | validar HB |
| 2026-08-15 | 19:40 | TEX@ATH | 2 TEX | 72.7% | 1.37 | 1.48 | 1.59 | fuera (pending 14) |

## Card 2026-08-11 — CERRADO

3W/5L · L200 · neto **−37.57**. Oficiales: CHC W · BOS L · TEX L · TB×2 W · HOU L. Fuera cashout: PHI −2.79 · AZ −2.79.
Oficial tras el día: **30/250** · 19W/11L · ROI +14.7% · neto +99.88.


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
| 19:38 | TEX @ LAA | TEX (2) | 1.71 | +12.5% | L25 | 5283372113 | **PERDIDO** −25 · score 3:2 | PREF ≥10% |
| 19:40 | COL @ AZ | AZ (1) | 1.55 | +0.7% | L25 | 5283375743 | CERRADO −2.79 | FUERA cashout |
| 19:40 | TB @ ATH | TB (2) | 1.60 | +18.0% | L25 | 5283377337 | **ABIERTO** | PREF ≥10% |
| 19:40 | TB @ ATH | TB (2) | 1.52 | +14.7% | L25 | 5285552204 | **ABIERTO** | PREF ≥10% · **2º ticket mismo partido 11 ago** |
| 19:45 | HOU @ SF | HOU (2) | 1.52 | +4.9% | L25 | 5283379280 | **PERDIDO** −25 · score 4:1 | oficial ≥3%; bajo mañana 5% |

**Abiertas (método) 11 ago:** L150 · incluye **2× TB@ATH** (L50 mismo juego).  
**Fuera cerradas hoy:** PHI −2.79 + AZ −2.79 = **−5.58** (no cuentan a oficial). Oficial sigue **24/250**.

### Seguimiento ABIERTAS — 2026-08-11 (L150 · 6 tickets; TB×2)

| Fecha | HN | Partido | Lado | Cuota | Edge real | Stake | Ticket | Nota |
|-------|----|---------|------|-------|-----------|-------|--------|------|
| 2026-08-11 | 16:45 | CHC@WSH | 2 CHC | 1.58 | +5.6% | L25 | 5283364050 | **GANADO** +14.70 · score 6:8 |
| 2026-08-11 | 17:07 | BOS@TOR | 2 BOS | 2.30 | +24.7% | L25 | 5283366437 | **PERDIDO** −25 · score 5:3 |
| 2026-08-11 | 19:38 | TEX@LAA | 2 TEX | 1.71 | +12.5% | L25 | 5283372113 | **PERDIDO** −25 · score 3:2 |
| 2026-08-11 | 19:40 | TB@ATH | 2 TB | 1.60 | +18.0% | L25 | 5283377337 | **GANADO** +15.15 · PA EP score 2:12 |
| 2026-08-11 | 19:40 | TB@ATH | 2 TB | 1.52 | +14.7% | L25 | 5285552204 | **GANADO** +13.16 · PA EP score 2:12 |
| 2026-08-11 | 19:45 | HOU@SF | 2 HOU | 1.52 | +4.9% | L25 | 5283379280 | **PERDIDO** −25 · score 4:1 |

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
