# MLB Alert Bot (Hondubet forward test)

Bot de alertas MLB (Elo + value bet) con Telegram. Pensado para correr **24/7 en una PC siempre encendida**.

## En la PC que siempre esta encendida (una sola vez)

```powershell
git clone https://github.com/df4539-maker/mlb-alert-bot.git
cd mlb-alert-bot
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y pon tu `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`.

Descarga datos MLB (la primera vez tarda un poco):

```powershell
python main.py fetch
python main.py backtest --mode live
```

## Dejar el agente 24/7 (Telegram)

En esa PC, deja corriendo el listener (responde a `actualizar`, `aposte`, `gane`, `perdi`):

```powershell
python main.py listen
```

Opcional — tareas diarias 10:00 y 16:00 (Programador de tareas):

```powershell
schtasks /Create /TN "MLB_Bot_Manana" /TR "E:\ruta\mlb-alert-bot\scripts\run_bot_telegram.bat" /SC DAILY /ST 10:00 /F
schtasks /Create /TN "MLB_Bot_Tarde" /TR "E:\ruta\mlb-alert-bot\scripts\run_bot_telegram.bat" /SC DAILY /ST 16:00 /F
```

Ajusta la ruta del `.bat` a donde clonaste el repo. Edita el `.bat` si usas `.venv` (activa el venv antes de `python`).

## Comandos Telegram (celular)

| Escribes | Que hace |
|----------|----------|
| `actualizar` | Senales pre-match / no apostar si ya inicio |
| `aposte BOS LAD away 2.55 5` | Registra apuesta real |
| `gane BOS LAD` / `perdi BOS LAD` | Cierra resultado |
| `ayuda` | Ayuda |

## Estrategia (resumen)

- Modelo Elo MLB
- Value bet si edge >= 3% vs cuota ref. -110
- Solo pre-partido (no EN VIVO)
- Ejecucion manual en Hondubet

## PC de analisis

Puedes clonar el mismo repo en otra PC solo para revisar backtest / codigo. El **listener 24/7** debe vivir en la PC siempre encendida.
