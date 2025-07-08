import os
import argparse
import sys
from googleapiclient.http import MediaFileUpload

from ..utils.config import VIDEO_EXTENSIONS
from ..utils.file_utils import (
    record_uploaded_video,
    save_iframe_json,
    load_uploaded_log,
)
from .youtube_api import get_authenticated_service


# ---------------- Upload ----------------
def upload_video(youtube, file_path, title):
    print(f"📤 Uploading: {file_path}")
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title},
                "status": {
                    "privacyStatus": "unlisted",
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=media,
        )

        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"  ⏳ Progress: {int(status.progress() * 100)}%")
            except Exception as e:
                print(f"❌ Error during upload chunk: {e}")
                return False

        if response:
            video_id = response.get("id")
            print("  ✅ Successfully uploaded.")
            return video_id

    except Exception as e:
        print(f"❌ Error uploading video '{file_path}': {e}")
    return False


# ---------------- Batch upload ----------------
def upload_all_videos(folder_path):
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"❌ Error authenticating YouTube service: {e}")
        return []

    uploaded = load_uploaded_log()
    videos_id = []

    for file_name in os.listdir(folder_path):
        if any(file_name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            full_path = os.path.join(folder_path, file_name)
            if full_path in uploaded:
                print(f"⏭️ Already uploaded, skipping: {file_name}")
                continue

            title = os.path.splitext(file_name)[0]
            try:
                video_id = upload_video(youtube, full_path, title)
                if video_id:
                    record_uploaded_video(full_path)
                    videos_id.append(video_id)
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {e}")
    return videos_id


# ---------------- CLI ----------------
def main(args=None):
    parser = argparse.ArgumentParser(description="Upload Zoom videos to YouTube")
    parser.add_argument("--file", help="Path to video file (for single upload)")
    parser.add_argument("--folder", help="Path to folder with videos (for batch upload)")
    parser.add_argument("--title", help="Optional title for the video (only used with --file)")

    args = parser.parse_args(args)

    try:
        if not args.file and not args.folder:
            parser.error("You must specify --file (single upload) or --folder (batch upload).")

        if args.title and not args.file:
            parser.error("--title can only be used with --file.")

        if args.file:
            if not os.path.exists(args.file):
                parser.error(f"File does not exist: {args.file}")
            if not os.path.isfile(args.file):
                parser.error("--file must be a valid file, not a directory.")

            youtube = get_authenticated_service()
            title = args.title or os.path.splitext(os.path.basename(args.file))[0]
            video_id = upload_video(youtube, args.file, title)
            if video_id:
                record_uploaded_video(args.file)

        if args.folder:
            if not os.path.exists(args.folder):
                parser.error(f"Folder does not exist: {args.folder}")
            if not os.path.isdir(args.folder):
                parser.error("--folder must be a valid directory.")

            upload_all_videos(args.folder)

    except KeyboardInterrupt:
        print("\n User interruption.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
