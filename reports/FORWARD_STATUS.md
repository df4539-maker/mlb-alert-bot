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

**Pendientes:** 0 · exposición **0/4** (antes del card 17).

---

## Card Lun 17 ago 2026 (PRE-MATCH · en curso)

**Exposición:** **3/4** · L75 · cabe **1** · con 3: **solo PREF (≥10%)** · stake L25 · bank ~L1543.

### Apostadas (ABIERTO)
| Ticket | Partido | Lado | Cuota HB | Stake | P | Edge | Si gana | Si pierde | Nota |
|--------|---------|------|----------|-------|---|------|---------|-----------|------|
| 5303629617 | ATL @ MIN | **2 ATL** | 1.80 | L25 | 64.0% | +8.4% | **+20.00** | −25 | mid · ya puesta · HB&lt;2* |
| 5303632185 | DET @ PIT | **2 DET** | 1.83 | L25 | 63.7% | +9.1% | **+20.75** | −25 | mid · ya puesta · HB&lt;2* |
| 5303633055 | SD @ NYM | **2 SD** | 2.00 | L25 | 61.2% | +11.2% | **+25.00** | −25 | **PREF** · cumple ≥2.00 |

\*Puestas antes de la consigna cuota≥2.00; se respetan. Nuevas: solo HB≥2.00.

### SKIP
| Partido | Motivo |
|---------|--------|
| LAD @ COL · 2 LAD | HB 1.38 · edge −2.3% · cara |

### Último cupo (solo si edge real ≥+10%)
| Partido | Apuesta | P | Cuota mod | Mín HB ≥10% | Hora |
|---------|---------|---|-----------|-------------|------|
| BAL @ TB | **1 TB** | 58.3% | 1.72 | **≥2.07** | 16:05 |

Si TB &lt; 2.07 → no llenar el 4º (regla: con 3 solo PREF). Con 4 → stop.

### Pie de reglas
- Solo CON · PRE-MATCH · edge real = P − 1/HB · máx 4 · L25
- Preferencia ≥10%; mid 3–10% si hay hueco
- **CONSIGNA (desde 16 ago noche): cuota HB ≥ 2.00** (ganancia ≥ stake). Si HB &lt; 2.00 → **SKIP** aunque haya edge.

### Nota abiertas 17 ago (antes de la consigna cuota≥2)
ATL 1.80 y DET 1.83 **ya estaban puestas** → se respetan.  
SD 2.00 cumple.  
De aquí en adelante: no nuevas con HB &lt; 2.00 (TB u otras).

CSV: `data/forward_bets.csv` · Rutina: `reports/RUTINA.md`
