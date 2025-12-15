import requests
import os
from pathlib import Path
from typing import Optional, List
from zoomtube.utils.logger import logger
from zoomtube import config

ZOOM_API_BASE = "https://api.zoom.us/v2"


def get_access_token(
    account_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> str:
    account_id = account_id or config.ZOOM_ACCOUNT_ID
    client_id = client_id or config.ZOOM_CLIENT_ID
    client_secret = client_secret or config.ZOOM_CLIENT_SECRET

    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
    resp = requests.post(url, auth=(client_id, client_secret))
    resp.raise_for_status()

    token = resp.json()["access_token"]
    logger.debug("Access token obtenido correctamente")
    return token


def list_users(token: str) -> List[dict]:
    url = f"{ZOOM_API_BASE}/users"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("users", [])


def list_recordings(
    token: str,
    user_id: str,
    start_date: str,
    end_date: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
) -> List[dict]:
    """
    Devuelve la lista de reuniones con TODAS sus grabaciones.
    El filtrado por tipo/preferencia se hace en download.py.
    """
    end_date = end_date or start_date
    url = f"{ZOOM_API_BASE}/users/{user_id}/recordings?from={start_date}&to={end_date}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    meetings = resp.json().get("meetings", [])

    filtered = []
    for m in meetings:
        duration = m.get("duration", 0)
        if min_duration and duration < min_duration:
            continue
        if max_duration and duration > max_duration:
            continue

        files = m.get("recording_files", [])
        if not files:
            continue

        # No filtrar tipos aquí: devolver todo
        m["recording_files"] = files
        filtered.append(m)

    return filtered


def download_recording(token: str, file_url: str, dest_path: Path) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    with requests.get(file_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
            f.flush()
            os.fsync(f.fileno())
    logger.info(f"Grabación guardada en {dest_path}")
