import os
from datetime import datetime, timedelta
from . import zoom_api
from ..utils import file_utils
from ..utils.config import (
    ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, RECORDINGS_BASE_PATH
)
from ..utils.validations import is_valid_date_format


def select_preferred_recording(files):
    """Selecciona la mejor grabación MP4 basada en prioridad."""
    for view_type in ["shared_screen_with_gallery_view", "shared_screen_with_speaker_view"]:
        preferred = next(
            (f for f in files if f.get("file_type") == "MP4" and f.get("recording_type") == view_type),
            None
        )
        if preferred:
            return preferred
    return None


def get_unique_filename(output_path, base_name):
    """Avoid overwriting existing files by generating a unique name."""
    counter = 1
    file_path = os.path.join(output_path, base_name)
    name, ext = os.path.splitext(base_name)
    while os.path.exists(file_path):
        file_path = os.path.join(output_path, f"{name} ({counter}){ext}")
        counter += 1
    return file_path


def download_recordings(date, output_path, token, users: list, min_duration=10):
    """Download Zoom recordings for all users by filtering by minimum length."""
    for user in users:
        user_id = user.get("id")
        if not user_id:
            continue

        try:
            meetings = zoom_api.get_recordings(token, user_id, date)
        except Exception as e:
            print(f" Error getting recordings from user {user_id}: {e}")
            continue

        for meeting in meetings:
            try:
                duration = meeting.get("duration", 0)
                if duration < min_duration:
                    continue

                preferred = select_preferred_recording(meeting.get("recording_files", []))
                if not preferred:
                    continue

                topic = file_utils.sanitize_filename(meeting.get("topic", "sin_titulo"))
                file_url = preferred.get("download_url")
                if not file_url:
                    print(f"Recording invalid URL: {topic}")
                    continue

                file_path = get_unique_filename(output_path, f"{topic}.mp4")

                print(f"Downloading: {file_path}")
                zoom_api.download_recording(file_url, file_path, token)

            except Exception as e:
                print(f" Error processing meeting for user {user_id}: {e}")
                continue


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Download Zoom recordings")
    parser.add_argument("--date", help="Date for recordings (format: YYYY-MM-DD)")
    parser.add_argument("--output-path", help="Folder to save the downloaded Zoom recordings")
    parser.add_argument("--min-duration", type=int, default=10, help="Minimum duration in minutes (default: 10)")

    args = parser.parse_args()

    try:
        date = args.date or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if not is_valid_date_format(date, "%Y-%m-%d"):
            parser.error("Date format must be YYYY-MM-DD")

        output_path = args.output_path or os.path.join(RECORDINGS_BASE_PATH, date.replace("/", "-"))
        os.makedirs(output_path, exist_ok=True)

        token = zoom_api.get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
        users = zoom_api.get_users(token)

        download_recordings(date, output_path, token, users, args.min_duration)

    except KeyboardInterrupt:
        print("\n User interruption.")
        sys.exit(1)
    except Exception as e:
        print(f" Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
