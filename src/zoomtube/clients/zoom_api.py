# utils/zoom_api.py

import requests

def get_access_token(account_id, client_id, client_secret):
    """
    Solicita un token de acceso OAuth a la API de Zoom.
    """
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
    response = requests.post(url, auth=(client_id, client_secret))
    return response.json().get("access_token")

def get_users(token):
    """
    Devuelve una lista de usuarios asociados a la cuenta de Zoom.
    """
    url = "https://api.zoom.us/v2/users"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("users", [])

def get_recordings(token, user_id, from_date):
    """
    Devuelve una lista de reuniones grabadas para un usuario y fecha.
    """
    url = f"https://api.zoom.us/v2/users/{user_id}/recordings?from={from_date}&to={from_date}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("meetings", [])

def download_recording(file_url, file_name, token):
    """
    Descarga un archivo de grabación MP4 de Zoom a disco.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(file_url, headers=headers, stream=True)
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)