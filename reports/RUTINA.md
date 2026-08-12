# Rutina forward test MLB (3 PCs)

Repo: https://github.com/df4539-maker/mlb-alert-bot

## Roles

| PC | Rol |
|----|-----|
| **Compu de los bots** | `listen` 24/7 · alertas · registra apuestas · **push** a GitHub |
| **Compu de viaje** | Cursor / revisar · **no** `listen` · solo `git pull` |
| **Compu de la casa** | Análisis / proyectos nuevos · **no** `listen` |

## Rutina diaria (bots)

### Mañana 6:00–7:00
1. Usuario pasa **saldo** + “dame el día”.
2. Bot/agente arma top **5–10** value del mismo día (PRE-MATCH).
3. **Formato FIJO del cuadro:** Fecha | HN | Partido | Lado | P | Mod | Mín ≥5% | Mín ≥10% | Hondubet | Edge real | ¿Apostar? | Stake.
   - Mod = 1/P. Mín = 1/(P − umbral). Si Hondubet ≤ Mod → no apostar. (Sin columna Mín ≥3%.)
4. Reglas **FIJAS** (siempre al pie del cuadro):
   - Solo **CON** (P ≥ 50%). CONTRA → nunca.
   - **Mañana (6–8 AM):** edge **≥ +5%** para entrar ya.
   - **Resto del día / contador 250:** edge **≥ +3%**.
   - **Preferencia:** priorizar **edge ≥ +10%**; listar igual el resto del filtro.
   - Stake **1–2% del bank**. Tope **L25**. Máx. 5 (bank chico) u 8–10.
   - Meta **250** = CON + edge≥3%.
   - Decisión en casa: comparar cuota Hondubet vs columnas **Mín ≥5% / ≥10%** (no vs edge del card −110).

### Noche 20:00–21:00
1. Cerrar ganó/perdió (foto / `gane` / `perdi`).
2. Actualizar `data/forward_bets.csv` y `reports/FORWARD_STATUS.md`.
3. Push a GitHub desde la PC de bots.

### Viaje / casa
```powershell
cd ruta\mlb-alert-bot
git pull origin master
```
Luego en Cursor: “actualizá” / leé `reports/FORWARD_STATUS.md`.

## Contador (solo “con” modelo, sin contra)

Al 2026-08-05: **6 / 250** · 3W/3L · stake L75 · neto +24.35 · ROI ~+32% (muestra chica).

Baseline backtest: win 55.9% · ROI +6.7%.

Ver detalle: `reports/FORWARD_STATUS.md`.
