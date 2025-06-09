import argparse
from src import download_zoom, upload_youtube
import os

def main():
    import sys
    import os
    from datetime import datetime
    from dotenv import load_dotenv
    import argparse

    parser = argparse.ArgumentParser(description="Automatiza descarga y subida de grabaciones de Zoom")
    parser.add_argument(
        "--action", 
        choices=["download", "upload", "all"], 
        required=True, 
        help="Action to perform: download, upload, or both"
    )
    parser.add_argument(
        "--folder", 
        help="Recording folder to upload (only applies to 'upload' or 'all')"
    )
    parser.add_argument(
        "--file",
        help="Path of the video file to upload (only applies to 'upload one')"
    )
    parser.add_argument(
        "--date",
        help="Date for download (format: YYYY-MM-DD)"
    )

    args = parser.parse_args()

    # Validar que --date esté presente y tenga formato correcto
    if args.action in ["download", "all"]:
        if not args.date:
            print("❌ The --date argument is required for 'download' and 'all' actions.")
            sys.exit(1)
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("❌ The --date format must be YYYY-MM-DD.")
            sys.exit(1)

    if args.action == "download":
        download_zoom(["--date", args.date])
    
    elif args.action == "upload":
        from dotenv import load_dotenv
        load_dotenv()
        BASE_PATH = os.getenv("RECORDINGS_BASE_PATH", "data/grabaciones")

        if not args.folder and not args.file and not args.date:
            print("❌ You must provide either --folder, --file, or --date to upload videos.")
            sys.exit(1)
        elif args.file:
            upload_youtube(["--mode", "single", "--file", args.file])
        else:
            folder_path = args.folder
            if not folder_path and args.date:
                # Validar formato fecha
                try:
                    datetime.strptime(args.date, "%Y-%m-%d")
                except ValueError:
                    print("❌ The --date format must be YYYY-MM-DD.")
                    sys.exit(1)
                folder_path = os.path.join(BASE_PATH, args.date)
            if not os.path.exists(folder_path):
                print(f"❌ Folder does not exist: {folder_path}")
                sys.exit(1)
            upload_youtube(["--mode", "batch", "--folder", folder_path])

    elif args.action == "all":
        download_zoom(["--date", args.date])
        load_dotenv()
        BASE_PATH = os.getenv("RECORDINGS_BASE_PATH", "data/grabaciones")
        folder_path = os.path.join(BASE_PATH, args.date)
        upload_youtube(["--mode", "batch", "--folder", folder_path])



if __name__ == "__main__":
    main()
