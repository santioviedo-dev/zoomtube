from .uploads import Uploads
from .downloads import Downloads
from .recordings import Recordings

uploads = Uploads()
downloads = Downloads()
recordings = Recordings()

__all__ = ["uploads", "downloads", "recordings", "Uploads", "Downloads", "Recordings"]