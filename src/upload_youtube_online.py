from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

CLIENT_SECRETS_FILE = "client_secret_799050072364-beg7l7sjff06ev59dt5qidp3ambbh45g.apps.googleusercontent.com.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
TOKEN_FILE = "token.pickle"

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
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("🔗 Visitá este link para autorizar el acceso:")
            print(auth_url)
            code = input("🔐 Pegá acá el código de autorización: ")
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def upload_video(youtube, file_path, title):
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
            },
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
            print(f"Subiendo: {int(status.progress() * 100)}%")

    return response

if __name__ == "__main__":
    youtube = get_authenticated_service()
    video_path = r"D:\scripting\grabaciones\2025-06-04\Ingeniería de Software 4-6-2025.mp4"
    title = "Ingeniería de Software 4-6-2025"
    upload_video(youtube, video_path, title)
    print("✅ ¡Video subido exitosamente!")
