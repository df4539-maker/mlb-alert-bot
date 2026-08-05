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
3. Cuadro: partido, lado 1/2, P modelo, edge, stake sugerido.
4. Reglas a recordar siempre:
   - No apostar si **P &lt; 50%** (contra el modelo).
   - Preferir **edge ≥ +3%** vs cuota real.
   - Stake **1–2% del bank**.
   - Máx. 5 picks si bank chico; 8–10 si hay margen.
   - Meta **250** operaciones “con modelo” (+ value) antes de decidir.

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
