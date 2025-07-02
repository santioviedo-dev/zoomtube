import os
import argparse
from googleapiclient.http import MediaFileUpload
from ..utils.config import  VIDEO_EXTENSIONS
from .youtube_api import get_authenticated_service
from ..utils.file_utils import record_uploaded_video, save_iframe_json, load_uploaded_log

# ---------------- Upload ----------------
def upload_video(youtube, file_path, title):
    print(f"📤 Uploading: {file_path}")
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {
                "privacyStatus": "unlisted",
                "selfDeclaredMadeForKids": False,
            }
        },
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  ⏳ Progress: {int(status.progress() * 100)}%")

    if response:
        video_id = response.get("id")
        print("  ✅ Successfully uploaded.")
        return video_id
    return False

# ---------------- Batch mode ----------------
def upload_all_videos(folder_path):
    youtube = get_authenticated_service()
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
                if video_id := upload_video(youtube, full_path, title):
                    record_uploaded_video(full_path)
                    videos_id.append(video_id)
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {e}")
    return videos_id

# ---------------- CLI ----------------
def main(args=None):

    parser = argparse.ArgumentParser(description="Upload Zoom videos to YouTube")
    parser.add_argument("--file", help="Path to video file (for single mode)")
    parser.add_argument("--folder", help="Path to folder with videos (for batch mode)")
    parser.add_argument("--title", help="Title for the video (optional, only used with --file)")

    args = parser.parse_args(args) 

    if not args.file and not args.folder:
        parser.error("You must specify --file (single upload) or --folder (batch upload).")
    
    if args.title and not args.file:
        parser.error("--title can only be used with --file")
    
    if args.file:
        youtube = get_authenticated_service()
        title = (
            os.path.splitext(os.path.basename(args.file))[0] 
            if not args.title 
            else args.title
        )
        if upload_video(youtube, args.file, title):
            record_uploaded_video(args.file)

    if args.folder:
        folder_path = args.folder
        if not os.path.exists(folder_path):
            parser.error(f"Folder does not exist: {folder_path}")
            return
        upload_all_videos(folder_path)

if __name__ == "__main__":
    main()