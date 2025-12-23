# src/zoomtube/clients/zoom.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List, Dict

import requests

from zoomtube.utils.logger import logger
from zoomtube import config

ZOOM_API_BASE = "https://api.zoom.us/v2"


# =========================
# Helpers internos (core)
# =========================

def _get_access_token_core(account_id: str, client_id: str, client_secret: str) -> str:
    url = (
        "https://zoom.us/oauth/token"
        f"?grant_type=account_credentials&account_id={account_id}"
    )
    resp = requests.post(url, auth=(client_id, client_secret))
    resp.raise_for_status()
    return resp.json()["access_token"]


def _list_users_core(session: requests.Session, token: str) -> List[Dict]:
    url = f"{ZOOM_API_BASE}/users"
    headers = {"Authorization": f"Bearer {token}"}
    resp = session.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("users", [])


def _list_recordings_core(
    session: requests.Session,
    token: str,
    user_id: str,
    start_date: str,
    end_date: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
) -> List[Dict]:
    end_date = end_date or start_date
    url = f"{ZOOM_API_BASE}/users/{user_id}/recordings?from={start_date}&to={end_date}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = session.get(url, headers=headers)
    resp.raise_for_status()

    meetings = resp.json().get("meetings", [])
    filtered: List[Dict] = []

    for m in meetings:
        duration = m.get("duration", 0)

        if min_duration is not None and duration < min_duration:
            continue
        if max_duration is not None and duration > max_duration:
            continue

        files = m.get("recording_files", [])
        if not files:
            continue

        m["recording_files"] = files
        filtered.append(m)

    return filtered


def _download_recording_core(
    session: requests.Session,
    token: str,
    file_url: str,
    dest_path: Path,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    with session.get(file_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
            f.flush()
            os.fsync(f.fileno())


# =========================
# API pública (OO)
# =========================

class ZoomClient:
    """
    Cliente oficial de Zoom para el proyecto.
    - Encapsula credenciales (config)
    - Maneja/cacha token
    - Reusa conexiones con requests.Session()
    - Expone métodos sin "token plumbing"
    """

    def __init__(
        self,
        account_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.account_id = account_id or config.ZOOM_ACCOUNT_ID
        self.client_id = client_id or config.ZOOM_CLIENT_ID
        self.client_secret = client_secret or config.ZOOM_CLIENT_SECRET

        self._token: Optional[str] = token
        self._session: requests.Session = session or requests.Session()

    def get_access_token(self, force_refresh: bool = False) -> str:
        if self._token is not None and not force_refresh:
            return self._token

        self._token = _get_access_token_core(
            self.account_id, self.client_id, self.client_secret
        )
        logger.debug("Access token obtenido correctamente")
        return self._token

    def list_users(self) -> List[Dict]:
        token = self.get_access_token()
        return _list_users_core(self._session, token)

    def list_recordings(
        self,
        user_id: str,
        start_date: str,
        end_date: Optional[str] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ) -> List[Dict]:
        token = self.get_access_token()
        return _list_recordings_core(
            session=self._session,
            token=token,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_duration=min_duration,
            max_duration=max_duration,
        )

    def download_recording(self, file_url: str, dest_path: Path) -> None:
        token = self.get_access_token()
        _download_recording_core(self._session, token, file_url, dest_path)
        logger.info(f"Grabación guardada en {dest_path}")
