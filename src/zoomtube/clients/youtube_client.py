# src/zoomtube/clients/youtube_client.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from zoomtube.utils.logger import logger
from zoomtube import config


def _load_credentials():
    """
    Carga credenciales desde token.pickle o inicia flujo OAuth.
    """
    creds = None
    if os.path.exists(config.YOUTUBE_TOKEN_FILE):
        try:
            with open(config.YOUTUBE_TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
        except Exception as e:
            logger.warning(f"Token inválido o corrupto, se regenerará: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refrescando token de YouTube…")
            creds.refresh(Request())
        else:
            logger.info("Iniciando flujo OAuth de YouTube…")
            flow = InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRETS, config.SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Guardar credenciales
        with open(config.YOUTUBE_TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
            logger.debug(f"Token guardado en {config.YOUTUBE_TOKEN_FILE}")

    return creds


def get_authenticated_service():
    """
    Devuelve un cliente autenticado de YouTube API.
    """
    creds = _load_credentials()
    return build(config.API_SERVICE_NAME, config.API_VERSION, credentials=creds)
