# src/zoomtube/clients/__init__.py

from .zoom import ZoomClient
from .youtube import YouTubeClient

# Instancias "oficiales" reutilizables en todo el proyecto
zoom_client = ZoomClient()
youtube_client = YouTubeClient()

__all__ = [
    "ZoomClient",
    "YouTubeClient",
    "zoom_client",
    "youtube_client",
]
