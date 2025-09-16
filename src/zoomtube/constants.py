ZOOM_RECORDING_TYPES = [
    "shared_screen_with_speaker_view",
    "shared_screen_with_gallery_view",
    "active_speaker",
    "gallery_view",
    "audio_only",
    "chat_file",
    "timeline"
]

DEFAULT_PREFERRED_TYPES = [
    "shared_screen_with_speaker_view",
    "shared_screen_with_gallery_view",
    "shared_screen_only",
    "gallery_view",
    "speaker_view",
]

VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]


DEFAULT_SILENCE_THRESHOLD_DB = -35   # más negativo = más estricto
DEFAULT_SILENCE_RATIO = 0.9          # 90% de silencio como máximo tolerado