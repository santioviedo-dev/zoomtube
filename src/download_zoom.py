import requests
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

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
    url = f"https://api.zoom.us/v2/users/{user_id}/recordings?from={from_date}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    return response.json().get("meetings", [])

def download_recording(file_url, file_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(file_url, headers=headers, stream=True)
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def main():
    token = get_access_token()
    users = get_users(token)

    from_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    base_dir = os.path.join("grabaciones", from_date)
    os.makedirs(base_dir, exist_ok=True)

    for user in users:
        user_id = user["id"]
        
        meetings = get_recordings(token, user_id, from_date)
        for meeting in meetings:
            duration = meeting.get("duration", 0)
            recording_files = meeting.get("recording_files", [])
            
            if duration < 20:
                continue  # Ignora reuniones cortas 

            # Primero busca vista con galería
            preferred = next(
                (f for f in recording_files 
                if f["file_type"] == "MP4" and f["recording_type"] == "shared_screen_with_gallery_view"),
                None
            )

            # Si no hay, busca vista con orador
            if not preferred:
                preferred = next(
                    (f for f in recording_files 
                    if f["file_type"] == "MP4" and f["recording_type"] == "shared_screen_with_speaker_view"),
                    None
                )

            if preferred:
                topic = meeting["topic"]  # No se reemplazan espacios
                file_url = preferred["download_url"]

                # Armar nombre base sin ID ni tipo
                base_filename = f"{topic}.mp4"
                file_path = os.path.join(base_dir, base_filename)

                # Agregar sufijo si ya existe
                counter = 1
                while os.path.exists(file_path):
                    base_filename = f"{topic} ({counter}).mp4"
                    file_path = os.path.join(base_dir, base_filename)
                    counter += 1

                print(f"Descargando: {file_path}")
                download_recording(file_url, file_path, token)


if __name__ == "__main__":
    main()
