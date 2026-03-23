from .uploads import UploadRegistry
from .downloads import DownloadRegistry
from .recordings import RecordingRegistry

uploads = UploadRegistry()
downloads = DownloadRegistry()
recordings = RecordingRegistry()

__all__ = ["uploads", "downloads", "recordings", "Uploads", "Downloads", "Recordings"]