from argparse import ArgumentParser
from zoomtube.pipeline import download, upload, process
import zoomtube.constants as constants
from zoomtube.utils.logger import get_logger


def main():
    p = ArgumentParser(prog="zoomtube")

    # Flags globales de logging
    p.add_argument("--verbose", action="store_true", help="Mostrar logs DEBUG en consola")
    p.add_argument("--quiet", action="store_true", help="Mostrar solo errores en consola")

    sub = p.add_subparsers(dest="cmd", required=True)

    # --- download ---
    dl = sub.add_parser("download", help="Download Zoom recordings")
    dl.add_argument("--start-date")
    dl.add_argument("--end-date")
    dl.add_argument("--date", help="Shortcut: download only this date (YYYY-MM-DD)")
    dl.add_argument("--min-duration", type=int, default=10)
    dl.add_argument("--max-duration", type=int)
    dl.add_argument("--output-path")

    # Dos modos de selección de grabación
    dl.add_argument("--recording-type", nargs="+", choices=constants.ZOOM_RECORDING_TYPES,
                    help="Descargar todas las grabaciones que coincidan con los tipos")
    dl.add_argument("--recording-type-preferred", nargs="+", choices=constants.ZOOM_RECORDING_TYPES,
                    help="Descargar solo la primera grabación encontrada según orden de preferencia")

    # Flags para análisis de audio
    dl.add_argument("--check-audio", action="store_true",
                    help="Verificar que las grabaciones tengan audio suficiente", default=True)
    dl.add_argument("--silence-threshold", type=int,
                    default=constants.DEFAULT_SILENCE_THRESHOLD_DB,
                    help="Umbral de silencio en dB (default: -35)")
    dl.add_argument("--silence-ratio", type=float,
                    default=constants.DEFAULT_SILENCE_RATIO,
                    help="Proporción máxima de silencio tolerada (default: 0.9)")

    # --- upload ---
    upload_parser = sub.add_parser("upload", help="Upload videos to YouTube")
    upload_sub = upload_parser.add_subparsers(dest="mode", required=True)

    single = upload_sub.add_parser("file", help="Upload a single video")
    single.add_argument("path", help="Path to video file")
    single.add_argument("--title", required=False)
    single.add_argument("--description", default="")
    single.add_argument("--tags", nargs="+", default=[])
    single.add_argument("--privacy-status", choices=["public", "private", "unlisted"], default="unlisted")
    single.add_argument("--playlist-id")
    single.add_argument("--schedule")

    batch = upload_sub.add_parser("folder", help="Upload multiple videos from a folder")
    batch.add_argument("path", help="Path to folder")
    batch.add_argument("--privacy-status", choices=["public", "private", "unlisted"], default="unlisted")
    batch.add_argument("--playlist-id")
    batch.add_argument("--tags", nargs="+", default=[])
    batch.add_argument("--description", default="")
    # batch.add_argument("--metadata-csv")

    # --- process ---
    proc = sub.add_parser("process", help="Download and upload in one step")
    proc.add_argument("--date", help="Date to process (YYYY-MM-DD). Default: yesterday")
    proc.add_argument("--check-audio", action="store_true", default=True,
                      help="Verificar que las grabaciones tengan audio suficiente")

    args = p.parse_args()

    # --- Configurar logger según flags ---
    logger = get_logger(verbose=args.verbose, quiet=args.quiet)

    # --- Dispatch ---
    if args.cmd == "download":
        logger.info("Iniciando descarga de grabaciones...")

        if args.recording_type and args.recording_type_preferred:
            logger.error("No se puede usar --recording-type y --recording-type-preferred al mismo tiempo")
            return

        download.run(
            start_date=args.start_date,
            end_date=args.end_date,
            date=args.date,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            output_path=args.output_path,
            recording_types=args.recording_type,
            preferred_types=args.recording_type_preferred,
            check_audio=args.check_audio,
            silence_threshold=args.silence_threshold,
            silence_ratio=args.silence_ratio,
        )

    elif args.cmd == "upload":
        if args.mode == "file":
            logger.info(f"Subiendo archivo: {args.path}")
            upload.run_single(
                path=args.path,
                title=args.title,
                description=args.description,
                tags=args.tags,
                privacy_status=args.privacy_status,
                playlist_id=args.playlist_id,
                schedule=args.schedule,
            )
        elif args.mode == "folder":
            logger.info(f"Subiendo carpeta: {args.path}")
            upload.run_batch(
                folder=args.path,
                description=args.description,
                tags=args.tags,
                privacy_status=args.privacy_status,
                playlist_id=args.playlist_id,
                # metadata_csv=args.metadata_csv,
            )

    elif args.cmd == "process":
        logger.info("Ejecutando pipeline completo (descarga + subida)...")
        process.run(date=args.date, check_audio=args.check_audio)


if __name__ == "__main__":
    main()
