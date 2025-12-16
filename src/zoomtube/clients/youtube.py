from __future__ import annotations
import pickle
from pathlib import Path
from typing import Optional, List, Any, Dict

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from zoomtube.utils.logger import logger
from zoomtube import config


# =========================
# Helpers internos (core)
# =========================

def _load_credentials_core(
    token_file: Path,
    client_secrets_file: Path,
    scopes: List[str]
):
    """
    Carga credenciales desde token.pickle o inicia flujo OAuth.
    """
    creds = None
    if token_file.exists():
        try:
            with token_file.open("rb") as token:
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
                str(client_secrets_file), scopes
            )
            creds = flow.run_local_server(port=0)

        token_file.parent.mkdir(parents=True, exist_ok=True)
        with token_file.open("wb") as token:
            pickle.dump(creds, token)
            logger.debug(f"Token guardado en {token_file}")

    return creds


# =========================
# API pública (OO)
# =========================

class YoutubeClient:
    """
    Cliente de YouTube para el proyecto.
    - Encapsula OAuth/token
    - Cachea el service (build) para no reconstruirlo cada vez
    - Expone operaciones de negocio (ej: upload_video)
    """

    def __init__(
        self,
        token_file: Optional[Path] = None,
        client_secrets_file: Optional[Path] = None,
        scopes: Optional[List[str]] = None,
        api_service_name: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.token_file = Path(token_file or config.YOUTUBE_TOKEN_FILE)
        self.client_secrets_file = Path(client_secrets_file or config.YOUTUBE_CLIENT_SECRETS)
        self.scopes = scopes or list(config.SCOPES)
        self.api_service_name = api_service_name or config.API_SERVICE_NAME
        self.api_version = api_version or config.API_VERSION

        self._service = None

    def get_service(self, force_rebuild: bool = False):
        """
        Devuelve el objeto service de googleapiclient (YouTube).
        Si force_rebuild=True, vuelve a construirlo.
        """
        if self._service is not None and not force_rebuild:
            return self._service
        
        creds = _load_credentials_core(
            token_file=self.token_file,
            client_secrets_file=self.client_secrets_file,
            scopes=self.scopes
        )
        self._service = build(self.api_service_name, self.api_version, credentials=creds)
        return self._service

    def upload_video(
        self,
        file_path: Path,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        category_id: str = "27",
        privacy_status: str = "unlisted",
        chunksize: int = -1,
        resumable: bool = True,
    ) -> str:
        """
        Sube un video y devuelve el video_id.
        - category_id "27" = Education 
        - privacy_status: "private" | "unlisted" | "public"
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"No existe el archivo: {file_path}")
        
        youtube = self.get_service()

        body: Dict[str, Any] = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
            },
        }

        media = MediaFileUpload(str(file_path), chunksize=chunksize, resumable=resumable)

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress() * 100)}%")
        video_id = response.get("id")
        logger.info(f"Video subido correctamente: https://youtu.be/{video_id}")
        return video_id