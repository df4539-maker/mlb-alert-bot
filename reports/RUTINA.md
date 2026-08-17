# Rutina forward test MLB (3 PCs)

Repo: https://github.com/df4539-maker/mlb-alert-bot

## Roles

| PC | Rol |
|----|-----|
| **Compu de los bots** | `listen` 24/7 · Elo CSV mañana · registra tickets/cierres · **push** |
| **Compu de viaje** | Arma el **card diario** · `git pull` · **no** `listen` |
| **Compu de la casa** | Análisis / proyectos nuevos · **no** `listen` |

## Flujo card diario (desde ago 2026)

1. **Bots (mañana):** genera `data/predictions_YYYY-MM-DD.csv` (Elo PRE-MATCH, todos los juegos del día) → `git push` → avisa: *predicciones listas YYYY-MM-DD · commit xxx*
2. **Viaje:** `git pull` → aplica consignas (CON, edge 3/5/10%, máx 4, L25) + cuotas Hondubet → arma el **cuadro de 4**
3. **Bots:** `listen`, registrar tickets, cierres, push CSV/status
4. **Viaje:** **NO** `listen`

```powershell
# Bots — materia prima Elo
cd ruta\mlb-alert-bot
.\.venv\Scripts\python.exe scripts\export_daily_predictions.py --date YYYY-MM-DD
git add data/predictions_YYYY-MM-DD.csv
git commit -m "Predictions YYYY-MM-DD"
git push origin master
```

Columnas CSV: `date,away,home,side_con,P,cuota_modelo,hora_HN,game_pk`

## Rutina diaria (bots)

### Mañana 6:00–7:00
1. Generar predicciones Elo del día (`export_daily_predictions.py`) + push.
2. Viaje arma el card; bots no arma el cuadro de 4 (salvo pedido).
3. Consignas fijas (viaje aplica): CON only · mañana ≥5% · día ≥3% · prefer ≥10% · L25 · máx 4 abiertas / tope L125 · PRE-MATCH.

### Noche 20:00–21:00
1. Cerrar ganó/perdió (foto / `gane` / `perdi`).
2. Actualizar `data/forward_bets.csv` y `reports/FORWARD_STATUS.md`.
3. Push a GitHub desde la PC de bots.

### Viaje / casa
```powershell
cd ruta\mlb-alert-bot
git pull origin master
```
Leé `data/predictions_YYYY-MM-DD.csv` + `reports/FORWARD_STATUS.md`.

## Contador

Ver detalle actual: `reports/FORWARD_STATUS.md`.

Baseline backtest: win 55.9% · ROI +6.7%.
