from src.zoom import download_zoom as zoom, zoom_api
from src.youtube import upload_youtube as yt, youtube_api
import sys
import os
from datetime import datetime, timedelta
from src.utils.config import RECORDINGS_BASE_PATH, ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
from src.utils.validations import is_valid_date_format
from src.utils.file_utils import save_iframe_json, clean_iframe_json
import argparse

def do_download(date):
    token = zoom_api.get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    users = zoom_api.get_users(token)

    # Crear carpeta destino
    date_folder = date.replace("/", "-")
    output_path = os.path.join(RECORDINGS_BASE_PATH, date_folder)
    os.makedirs(output_path, exist_ok=True)

    # Verificar si ya hay archivos
    if os.listdir(output_path):  # si hay al menos un archivo o carpeta
        confirm = input(f"⚠️ La carpeta '{output_path}' ya contiene archivos. ¿Deseás continuar con la descarga en ese lugar? (s/n): ").strip().lower()
        if confirm not in ("s", "sí", "si", "y", "yes"):
            print("Descarga cancelada.")
            return [output_path]

    zoom.download_recordings(date, output_path, token, users)
    return output_path

def do_upload(folder=None, file=None, date=None, title=None):
        if file:
            youtube = youtube_api.get_authenticated_service()
            title = (
                os.path.splitext(os.path.basename(file))[0] 
                if not title 
                else title
            )
            video_id = list(yt.upload_video(youtube, file, title))
            # iframe = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen=""></iframe>'
            clean_iframe_json()
            save_iframe_json(video_id)
        elif date:
            date_folder = date.replace("/", "-")
            folder_path = os.path.join(RECORDINGS_BASE_PATH, date_folder)
            if os.path.exists(folder_path):
                videos_id = yt.upload_all_videos(folder_path)
                save_iframe_json(videos_id)
            else:
                print(f"Folder does not exist: {folder_path}")
                sys.exit(1)
        else:
            videos_id = yt.upload_all_videos(folder)
            save_iframe_json(videos_id)
def main():
    parser = argparse.ArgumentParser(description="Automatiza descarga y subida de grabaciones de Zoom")
    parser.add_argument(
        "--action", 
        choices=["download", "upload", "all"], 
        help="Action to perform: download, upload, or both",
        default="all"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--folder", 
        help="Recording folder to save recordings and upload (only applies to 'upload' or 'all')"
    )
    group.add_argument(
        "--file",
        help="Path of the video file to upload (only applies to 'upload')"
    )
    parser.add_argument(
        "--date",
        help="Date for download (format: YYYY-MM-DD)",
    )
    parser.add_argument(
        "--title",
        help="Title for the video (optional, only applies to 'upload one')"
    )
    args = parser.parse_args()
    
    date = args.date if args.date else (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if args.date:
        if is_valid_date_format(args.date, "%Y-%m-%d"):
            folder_path = os.path.join(RECORDINGS_BASE_PATH, args.date)
        else:
            parser.error("The date format is incorrect. You must enter 'YYYY-MM-DD'")
    
    if args.title and not args.file:
        parser.error("--title can only be used with --upload")
    if args.file and args.folder:
        parser.error("Only can use --file or --folder, not both.")
        
    
    if args.file and not os.path.exists(args.file):
        print(f"Folder does not exist: {args.file}")
        sys.exit(1)
    if args.folder and not os.path.exists(args.folder):
        print(f"❌ Folder does not exist: {args.folder}")
        sys.exit(1)
        
        
        
        
    if args.action == "all":
        output_path = do_download(date)
        if isinstance(output_path, list):
            print("Continuando con la subida de los videos...")
            output_path = output_path[0]
        # En all el folder viene de la descarga (o del argumento --folder si se especifica)
        folder_to_upload = args.folder if args.folder else output_path

        if not os.path.exists(folder_to_upload):
            parser.error(f"❌ The folder to upload not exist: {folder_to_upload}")

        do_upload(folder=folder_to_upload)
        
    if args.action == "download":
        do_download(date)
    
    elif args.action == "upload":
        if not (args.folder or args.file or date):
            parser.error("❌ You must provide either --folder, --file, or --date to upload videos.")
        


if __name__ == "__main__":
    main()
