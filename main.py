import argparse

from mlb.bot import run_bot
from mlb.config import DEFAULT_SEASONS
from mlb.fetch import fetch_seasons
from mlb.forward_log import log_bet, update_result
from mlb.predict import print_upcoming
from mlb.stats_eval import run_evaluation
from mlb.status_check import print_status
from mlb.telegram_listener import run_listener
from mlb.backtest import print_backtest_report, run_backtest


def main() -> None:
    parser = argparse.ArgumentParser(description="MLB Predictor — datos, backtest, bot de alertas")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_parser = sub.add_parser("fetch", help="Descargar datos de MLB Stats API")
    fetch_parser.add_argument(
        "--seasons",
        nargs="+",
        type=int,
        default=DEFAULT_SEASONS,
    )

    backtest_parser = sub.add_parser("backtest", help="Ejecutar backtest")
    backtest_parser.add_argument(
        "--mode",
        choices=["live", "walk_forward"],
        default="live",
        help="live = cronológico; walk_forward = entrena pasado, prueba temporada nueva",
    )
    backtest_parser.add_argument(
        "--min-edge",
        type=float,
        default=0.03,
        help="Edge mínimo para simular apuesta (ej. 0.03 = 3%%)",
    )
    backtest_parser.add_argument(
        "--no-betting",
        action="store_true",
        help="Solo métricas del modelo, sin simular apuestas",
    )

    sub.add_parser("backtest-all", help="Ejecuta live + walk_forward")

    predict_parser = sub.add_parser("predict", help="Predicciones partidos próximos")
    predict_parser.add_argument("--min-edge", type=float, default=0.03)

    bot_parser = sub.add_parser(
        "bot",
        help="Bot de alertas: value bets para operar en Hondubet",
    )
    bot_parser.add_argument("--min-edge", type=float, default=0.03)
    bot_parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Dias hacia adelante (0=solo hoy, 1=hoy+manana)",
    )
    bot_parser.add_argument("--stake", type=float, default=1.0, help="Unidades sugeridas")
    bot_parser.add_argument(
        "--all-games",
        action="store_true",
        help="Mostrar todos los partidos, no solo value bets",
    )
    bot_parser.add_argument(
        "--telegram",
        action="store_true",
        help="Enviar alerta a Telegram (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)",
    )
    bot_parser.add_argument(
        "--min-minutes",
        type=int,
        default=15,
        help="Solo alertar si faltan al menos N minutos para el inicio",
    )

    status_parser = sub.add_parser(
        "status",
        help="Revisar alertas: cuales aun no inician / cuales ya no apostar",
    )
    status_parser.add_argument("--telegram", action="store_true")

    sub.add_parser(
        "listen",
        help="Escucha Telegram: escribe 'actualizar' desde el celular",
    )
    eval_parser = sub.add_parser(
        "evaluate",
        help="LLN + hipotesis: ¿la estrategia es confiable?",
    )
    eval_parser.add_argument("--bankroll", type=float, default=500.0)
    eval_parser.add_argument("--stake", type=float, default=5.0)
    eval_parser.add_argument(
        "--assumed-edge",
        type=float,
        default=0.03,
        help="Edge de hit rate sobre break-even a detectar (0.03 = 3pp)",
    )
    eval_parser.add_argument(
        "--mode",
        choices=["live", "walk_forward"],
        default="live",
        help="CSV de backtest a evaluar",
    )

    log_parser = sub.add_parser("log-bet", help="Registrar apuesta real Hondubet (forward test)")
    log_parser.add_argument("--away", required=True, help="Visitante (ej. BOS)")
    log_parser.add_argument("--home", required=True, help="Local (ej. LAD)")
    log_parser.add_argument("--side", required=True, help="home|away o abreviatura apostada")
    log_parser.add_argument("--stake", type=float, default=5.0)
    log_parser.add_argument("--odds", type=float, default=None, help="Cuota decimal (ej. 2.55)")
    log_parser.add_argument("--american", type=float, default=None, help="Cuota americana opcional")
    log_parser.add_argument("--date", default=None, help="Fecha partido YYYY-MM-DD")
    log_parser.add_argument(
        "--result",
        default="pending",
        choices=["pending", "win", "loss"],
    )
    log_parser.add_argument("--notes", default="")

    settle_parser = sub.add_parser("settle-bet", help="Marcar win/loss de una apuesta pending")
    settle_parser.add_argument("--away", required=True)
    settle_parser.add_argument("--home", required=True)
    settle_parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    settle_parser.add_argument("--result", required=True, choices=["win", "loss"])

    run_parser = sub.add_parser("run", help="Fetch + backtest live")
    run_parser.add_argument("--seasons", nargs="+", type=int, default=DEFAULT_SEASONS)

    args = parser.parse_args()

    if args.command == "fetch":
        stats = fetch_seasons(args.seasons)
        print(f"\nListo: {stats['games']} partidos ({stats['final_games']} finales)")

    elif args.command == "backtest":
        result = run_backtest(
            mode=args.mode,
            min_edge=args.min_edge,
            simulate_betting=not args.no_betting,
        )
        print_backtest_report(result)

    elif args.command == "backtest-all":
        for mode in ("live", "walk_forward"):
            result = run_backtest(mode=mode, min_edge=0.03, simulate_betting=True)
            print_backtest_report(result)

    elif args.command == "predict":
        print_upcoming(min_edge=args.min_edge)

    elif args.command == "bot":
        run_bot(
            days_ahead=args.days,
            min_edge=args.min_edge,
            stake_units=args.stake,
            only_value=not args.all_games,
            send_to_telegram=args.telegram,
            min_minutes_before_start=args.min_minutes,
        )

    elif args.command == "status":
        print_status(send_to_telegram=args.telegram)

    elif args.command == "listen":
        run_listener()
    elif args.command == "evaluate":
        run_evaluation(
            bankroll=args.bankroll,
            stake=args.stake,
            assumed_edge=args.assumed_edge,
            backtest_mode=args.mode,
        )

    elif args.command == "log-bet":
        path = log_bet(
            away=args.away,
            home=args.home,
            side=args.side,
            stake=args.stake,
            decimal_odds=args.odds,
            american_odds=args.american,
            game_date=args.date,
            result=args.result,
            notes=args.notes,
        )
        print(f"Apuesta registrada en {path}")

    elif args.command == "settle-bet":
        n = update_result(args.away, args.home, args.date, args.result)
        if n:
            print(f"Actualizado: {args.away}@{args.home} {args.date} -> {args.result}")
        else:
            print("No se encontro apuesta pending coincidente.")

    elif args.command == "run":
        stats = fetch_seasons(args.seasons)
        print(f"\nDatos: {stats['games']} partidos")
        result = run_backtest(mode="live", min_edge=0.03)
        print_backtest_report(result)


if __name__ == "__main__":
    main()
