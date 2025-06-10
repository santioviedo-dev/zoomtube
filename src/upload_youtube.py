import os
import argparse
import pickle
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv(dotenv_path="../config/.env")
BASE_PATH = os.getenv("RECORDINGS_BASE_PATH")

# Ruta absoluta de este archivo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorios relativos
CONFIG_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../config"))
LOGS_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../logs"))
DATA_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../data"))
OUTPUT_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../output"))

# Configuration
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# File paths
CLIENT_SECRETS_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.pickle")
LOG_FILE = os.path.join(LOGS_DIR, "uploaded.log")
IFRAME_JSON_FILE = os.path.join(DATA_DIR, "iframes.json")
HTML_FILE = os.path.join(OUTPUT_DIR, "iframes_clean.html")

# ---------------- Autentication ----------------
def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

# ---------------- Registration and Log ----------------
def load_uploaded_log():
    return set(open(LOG_FILE, "r", encoding="utf-8").read().splitlines()) if os.path.exists(LOG_FILE) else set()

def record_uploaded_video(file_path):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(file_path + "\n")

# ---------------- Iframe ----------------
def save_iframe_json(title, iframe):
        
    data = []
    if os.path.exists(IFRAME_JSON_FILE):
        os.remove(IFRAME_JSON_FILE)
    data = {"title": title, "iframe": iframe}
    with open(IFRAME_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        

# ---------------- Subida ----------------
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
        iframe = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen=""></iframe>'
        save_iframe_json(title, iframe)
        print("  ✅ Successfully uploaded.")
        return True
    return False

# ---------------- Modo masivo ----------------
def upload_all_videos(folder_path):
    youtube = get_authenticated_service()
    uploaded = load_uploaded_log()

    for file_name in os.listdir(folder_path):
        if any(file_name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            full_path = os.path.join(folder_path, file_name)
            if full_path in uploaded:
                print(f"⏭️ Already uploaded, skipping: {file_name}")
                continue
            title = os.path.splitext(file_name)[0]
            try:
                if upload_video(youtube, full_path, title):
                    record_uploaded_video(full_path)
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {e}")


# ---------------- CLI ----------------
def main(args=None):

    parser = argparse.ArgumentParser(description="Upload Zoom videos to YouTube")
    parser.add_argument("--mode", choices=["single", "batch"], required=True, help="Upload mode: single or batch")
    parser.add_argument("--file", help="Path to video file (for single mode)")
    parser.add_argument("--folder", help="Path to folder with videos (for batch mode)")
    parser.add_argument("--date", help="Date in format YYYY-MM-DD (used to locate folder inside base path)")

    args = parser.parse_args(args) 

    if args.mode == "single":
        if not args.file:
            print("❌ You must specify --file when using 'single' mode")
            return
        youtube = get_authenticated_service()
        title = os.path.splitext(os.path.basename(args.file))[0]
        if upload_video(youtube, args.file, title):
            record_uploaded_video(args.file)

    elif args.mode == "batch":
        folder_path = args.folder
        if not folder_path:
            if not args.date:
                print("❌ You must specify --folder or --date when using 'batch' mode")
                return
            # Normalizar nombre de carpeta
            date_folder = args.date.replace("/", "-")
            folder_path = os.path.join(BASE_PATH, date_folder)
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder does not exist: {folder_path}")
            return

        upload_all_videos(folder_path)

if __name__ == "__main__":
    main()
