# Forward test — estado

## Filtro oficial (FIJO)

- Solo cuenta / solo apostar: **P modelo >= 50% (CON)** y **edge >= +3%** vs cuota real.
- CONTRA o CON sin value: fuera de protocolo.
- Meta **250** ops oficiales.
- Exposición: máx **4** abiertas · tope **L125** · stake L25 · bank ~L1543.

## Oficiales cerradas (notes CSV · CON + edge≥3%)

**Oficial:** 25W / 20L · stake L1055 · neto **+26.41** · ROI **+2.5%** · hit **55.6%** · contador **45 / 250**

(Viaje provisorio citó +24.55 / ROI +2.3%; bots con scores MLB API Aug 16 → **+26.41** / **+2.5%**. Misma 45 · 25W/20L.)

### Cuadro baseline (cerradas)

| Bucket | n | Record | Hit % | ROI % | Neto | Stake |
|--------|---|--------|-------|-------|------|-------|
| Baseline backtest | — | — | 55.9 | +6.7 | — | — |
| Todas | 59 | 31W/28L | 52.5 | −0.2 | −3.26 | L1305 |
| Solo CON | 57 | 30W/27L | 52.6 | +0.9 | +11.24 | L1275 |
| CON+edge≥3% (oficial) | **45** | **25W/20L** | **55.6** | **+2.5** | **+26.41** | **L1055** |
| Preferida ≥10% | 30 | 15W/15L | 50.0 | −2.0 | −14.51 | — |
| Oficial mid 3–10% | 15 | 10W/5L | 66.7 | +12.2 | +40.92 | — |

Baseline: win 55.9% · ROI +6.7%. Hit ≈ baseline; ROI bajo baseline. Muestra chica — **no cambiar método**.

### Cierre 16 ago (2W/2L · neto día −2.50)

| Ticket | Partido | Lado | Cuota | Res | Profit | Score |
|--------|---------|------|-------|-----|--------|-------|
| 5300300843 | BOS@PIT | 2 BOS | 1.83 | L | −25.00 | 3:8 |
| 5300346202 | NYY@TOR | 2 NYY | 2.10 | W | +27.50 | 4:3 |
| 5300360533 | TEX@ATH | 2 TEX | 1.71 | L | −25.00 | 2:5 |
| 5300307542 | KC@LAA | 2 KC | 1.80 | W | +20.00 | 3:0 |

**Pendientes:** 0 · exposición **0/4**.

---

## Card Lun 17 ago 2026 (PRE-MATCH · mañana)

**Exposición:** 0/4 · caben **4** · PREF primero · mid si hay hueco · stake L25 · bank ~L1543.

Hondubet aún no cargado en este card → Edge = vs ref −110; al reportar cuota: `edge real = P − 1/HB`. Si HB ≤ Mod → SKIP.

### 1) PREFERIDAS ≥ +10% (modelo vs −110)

| Partido | Apuesta | P | Cuota mod | Edge | Hora HN | Stake |
|---------|---------|---|-----------|------|---------|-------|
| LAD@COL | **2 LAD** | 70.2% | 1.42 | **+17.8%** | 18:40 | L25 |
| ATL@MIN | **2 ATL** | 64.0% | 1.56 | **+11.6%** | 17:40 | L25 |
| DET@PIT | **2 DET** | 63.7% | 1.57 | **+11.3%** | 17:05 | L25 |

Mín HB ≥10%: LAD **1.66** · ATL **1.85** · DET **1.86**.

### 2) Listadas +3% a &lt;10% (no preferidas · yo decido)

| Partido | Apuesta | P | Cuota mod | Edge | Hora HN | Stake |
|---------|---------|---|-----------|------|---------|-------|
| SD@NYM | **2 SD** | 61.2% | 1.63 | +8.8% | 17:10 | L25 |
| BAL@TB | **1 TB** | 58.3% | 1.72 | +5.9% | 16:05 | L25 |

Mín HB ≥5%: SD **1.78** · TB **1.88**.

### Top 4 para ocupar exposición (PREF primero)

1. **LAD@COL · 2 LAD** · 18:40 · PREF +17.8% · Mín≥10% 1.66  
2. **ATL@MIN · 2 ATL** · 17:40 · PREF +11.6% · Mín≥10% 1.85  
3. **DET@PIT · 2 DET** · 17:05 · PREF +11.3% · Mín≥10% 1.86  
4. **SD@NYM · 2 SD** · 17:10 · mid +8.8% · Mín≥5% 1.78 *(solo si las 3 PREF OK y queda 1 cupo)*

Con 0–2 abiertas: PREF primero, mid si hay hueco. Con 3: solo PREF. Con 4: stop.

### Pie de reglas

- Solo **CON** (P≥50%). Nunca CONTRA. Solo **PRE-MATCH** (si inició/warmup → no).
- Mañana: edge ≥ **+5%**. Contador 250: ≥ **+3%**. Preferencia: edge real ≥ **+10%**.
- `edge = P − 1/cuota_real`. Si HB acorta bajo umbral → **SKIP**. Si HB ≤ Mod → no.
- Stake **L25** · máx **4** abiertas · tope **L125** · no duplicar `away@home` abierto · suma ≤ ~8% bank.
- ¿Apostamos? → protocolo + exposición (SÍ / NO / espera).

CSV: `data/forward_bets.csv` · Rutina: `reports/RUTINA.md` · Tanking: `reports/tanking_baseline.html`
