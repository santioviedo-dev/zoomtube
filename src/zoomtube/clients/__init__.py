# src/zoomtube/clients/__init__.py

from .zoom import ZoomClient
from .youtube import YoutubeClient

# Instancias "oficiales" reutilizables en todo el proyecto
zoom_client = ZoomClient()
youtube_client = YoutubeClient()

__all__ = [
    "ZoomClient",
    "YoutubeClient",
    "zoom_client",
    "youtube_client",
]
