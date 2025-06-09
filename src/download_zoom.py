import requests
import os
import datetime
import argparse
from dotenv import load_dotenv
import re

# Ruta absoluta del script actual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta absoluta del archivo .env
ENV_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "../config/.env"))
load_dotenv(dotenv_path=ENV_PATH)

BASE_PATH = os.getenv("RECORDINGS_BASE_PATH")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET))
    return response.json().get("access_token")

def get_users(token):
    url = "https://api.zoom.us/v2/users"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("users", [])

def get_recordings(token, user_id, from_date):
    url = f"https://api.zoom.us/v2/users/{user_id}/recordings?from={from_date}&to={from_date}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("meetings", [])

def download_recording(file_url, file_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(file_url, headers=headers, stream=True)
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)  # Elimina caracteres inválidos
    name = name.strip()
    return name

def main(args=None):
    parser = argparse.ArgumentParser(description="Download Zoom recordings")
    parser.add_argument("--date", required=True, help="Date for recordings (format: YYYY-MM-DD)")
    args = parser.parse_args(args)

    # Validar formato de fecha
    try:
        datetime.datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD.")
        exit(1)

    # Crear carpeta destino
    date_folder = args.date.replace("/", "-")
    output_path = os.path.join(BASE_PATH, date_folder)
    os.makedirs(output_path, exist_ok=True)

    # Obtener token y usuarios
    token = get_access_token()
    users = get_users(token)

    for user in users:
        user_id = user["id"]
        meetings = get_recordings(token, user_id, args.date)

        for meeting in meetings:
            duration = meeting.get("duration", 0)
            recording_files = meeting.get("recording_files", [])

            if duration < 15:
                continue  # Ignora reuniones cortas

            # Buscar vista preferida
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
                topic = sanitize_filename(meeting.get("topic", "sin_titulo"))
                file_url = preferred["download_url"]
                base_filename = f"{topic}.mp4"
                file_path = os.path.join(output_path, base_filename)

                # Evitar sobrescritura
                counter = 1
                while os.path.exists(file_path):
                    base_filename = f"{topic} ({counter}).mp4"
                    file_path = os.path.join(output_path, base_filename)
                    counter += 1

                print(f"📥 Descargando: {file_path}")
                download_recording(file_url, file_path, token)

if __name__ == "__main__":
    main()
