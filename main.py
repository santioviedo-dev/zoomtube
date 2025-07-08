import argparse
import os
import sys
from datetime import datetime, timedelta

from src.utils.config import (
    RECORDINGS_BASE_PATH, ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
)
from src.utils.file_utils import clean_iframe_json, save_iframe_json
from src.utils.validations import is_valid_date_format
from src.youtube import upload_youtube as yt, youtube_api
from src.zoom import download_zoom as zoom, zoom_api


def do_download(date, min_duration=10, output_path=None):
    try:
        token = zoom_api.get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
        users = zoom_api.get_users(token)

        date_folder = date.replace("/", "-")
        output_path = os.path.join(RECORDINGS_BASE_PATH, date_folder) if not output_path else output_path
        os.makedirs(output_path, exist_ok=True)

        if os.listdir(output_path):
            confirm = input(
                f"⚠️ La carpeta '{output_path}' ya contiene archivos. ¿Deseás continuar con la descarga en ese lugar? (s/n): "
            ).strip().lower()
            if confirm not in ("s", "sí", "si", "y", "yes"):
                print("Descarga cancelada por el usuario.")
                return [output_path]

        zoom.download_recordings(date, output_path, token, users, min_duration)
        return output_path

    except Exception as e:
        print(f"Error durante la descarga: {e}")
        sys.exit(1)


def do_upload(folder=None, file=None, date=None, title=None):
    try:
        if file:
            youtube = youtube_api.get_authenticated_service()
            final_title = title or os.path.splitext(os.path.basename(file))[0]
            video_id = list(yt.upload_video(youtube, file, final_title))
            clean_iframe_json()
            save_iframe_json(video_id)
            return

        if date:
            folder_path = os.path.join(RECORDINGS_BASE_PATH, date.replace("/", "-"))
            if not os.path.exists(folder_path):
                print(f"La carpeta de grabaciones no existe: {folder_path}")
                sys.exit(1)
            folder = folder_path

        if folder:
            videos_id = yt.upload_all_videos(folder)
            save_iframe_json(videos_id)
        else:
            print("⚠️ Error: No se especificó ninguna carpeta ni archivo para subir.")
            sys.exit(1)

    except Exception as e:
        print(f"Error durante la subida: {e}")
        sys.exit(1)


def validate_paths(args, parser):
    if args.title and not args.file:
        parser.error("--title can only be used with --file")

    if args.file and args.folder:
        parser.error("You can only use --file or --folder, not both.")

    if args.file:
        if not os.path.exists(args.file):
            parser.error(f"File path does not exist: {args.file}")
        if not os.path.isfile(args.file):
            parser.error("The --file argument must be a file, not a directory.")

    if args.folder:
        if not os.path.exists(args.folder):
            parser.error(f"Folder path does not exist: {args.folder}")
        if not os.path.isdir(args.folder):
            parser.error("The --folder argument must be a directory.")

    if args.output_path and not os.path.exists(args.output_path):
        parser.error(f"Output path does not exist: {args.output_path}")


def main():
    parser = argparse.ArgumentParser(description="Automatiza descarga y subida de grabaciones de Zoom")
    parser.add_argument("--action", choices=["download", "upload", "all"], default="all")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--folder", help="Folder with videos to upload")
    group.add_argument("--file", help="Single video file to upload")

    parser.add_argument("--date", help="Date for download/upload (format: YYYY-MM-DD)")
    parser.add_argument("--title", help="Title for the video (only with --file)")
    parser.add_argument("--min-duration", type=int, default=10, help="Min duration in minutes (default: 10)")
    parser.add_argument("--output-path", help="Folder path to save the downloaded Zoom recordings")

    args = parser.parse_args()

    try:
        date = args.date or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        if not is_valid_date_format(date, "%Y-%m-%d"):
            parser.error("Date format must be 'YYYY-MM-DD'")

        validate_paths(args, parser)

        if args.action == "download":
            do_download(date, args.min_duration, args.output_path)

        elif args.action == "upload":
            if not (args.folder or args.file or args.date):
                parser.error("You must provide --folder, --file, or --date to upload.")
            do_upload(args.folder, args.file, date, args.title)

        elif args.action == "all":
            output_path = do_download(date, args.min_duration, args.output_path)
            if isinstance(output_path, list):  # Si se canceló la descarga
                output_path = output_path[0]
            folder_to_upload = args.folder or output_path
            do_upload(folder=folder_to_upload)

    except KeyboardInterrupt:
        print("\n Interrupción del usuario.")
        sys.exit(1)

    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
