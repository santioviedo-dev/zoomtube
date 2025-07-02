import os
import argparse
from datetime import datetime, timedelta
from . import zoom_api
from ..utils.config import ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, RECORDINGS_BASE_PATH
from ..utils import file_utils

# Download function

def download_recordings(date, output_path, token, users: list, min_duration=10):
    for user in users:
        user_id = user["id"]
        meetings = zoom_api.get_recordings(token, user_id, date)

        for meeting in meetings:
            duration = meeting.get("duration", 0)
            recording_files = meeting.get("recording_files", [])

            if duration < min_duration:
                continue

            preferred = next(
                (f for f in recording_files
                 if f["file_type"] == "MP4" and f["recording_type"] == "shared_screen_with_gallery_view"),
                None
            )
            if not preferred:
                preferred = next(
                    (f for f in recording_files
                     if f["file_type"] == "MP4" and f["recording_type"] == "shared_screen_with_speaker_view"),
                    None
                )

            if preferred:
                topic = file_utils.sanitize_filename(meeting.get("topic", "sin_titulo"))
                file_url = preferred["download_url"]
                base_filename = f"{topic}.mp4"
                file_path = os.path.join(output_path, base_filename)

                # Evitar sobrescritura
                counter = 1
                while os.path.exists(file_path):
                    base_filename = f"{topic} ({counter}).mp4"
                    file_path = os.path.join(output_path, base_filename)
                    counter += 1

                print(f"📥 Downloading: {file_path}")
                zoom_api.download_recording(file_url, file_path, token)
    

def main(args=None):
    parser = argparse.ArgumentParser(description="Download Zoom recordings")
    parser.add_argument("--date",
                        required=False,
                        help="Date for recordings (format: YYYY-MM-DD)")
    parser.add_argument("--output-path",
                        required=False,
                        help="Folder path to save the downloaded Zoom recordings")
    args = parser.parse_args(args)
    
    date = args.date if args.date else (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if not args.output_path:
        date_folder = date.replace("/", "-")
        output_path = os.path.join(RECORDINGS_BASE_PATH, date_folder)
        os.makedirs(output_path, exist_ok=True)
    else: output_path = args.output_path
    
    # Obtener token y usuarios
    token = zoom_api.get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    users = zoom_api.get_users(token)
    
    download_recordings(date, output_path, token, users)


if __name__ == "__main__":
    main()
