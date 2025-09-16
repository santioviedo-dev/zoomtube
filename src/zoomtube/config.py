# src/zoom2yt/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# --- Paths base ---
BASE_DIR = Path(__file__).resolve().parents[2]   # raíz del repo (nivel arriba de src/)
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

# --- Archivos especiales ---
LOG_FILE = LOGS_DIR / "last_uploaded.log"
IFRAME_JSON_FILE = DATA_DIR / "iframes.json"
HTML_FILE = OUTPUT_DIR / "iframes_clean.html"

# --- Archivos de YouTube ---
YOUTUBE_CLIENT_SECRETS = CONFIG_DIR / "client_secret.json"
YOUTUBE_TOKEN_FILE = CONFIG_DIR / "token.pickle"

# --- Cargar variables de entorno ---
# Prioridad: ~/.zoom2yt.env > .env local
GLOBAL_ENV = Path.home() / ".zoom2yt.env"
LOCAL_ENV = BASE_DIR / ".env"

if GLOBAL_ENV.exists():
    load_dotenv(GLOBAL_ENV)
if LOCAL_ENV.exists():
    load_dotenv(LOCAL_ENV, override=True)

# --- Variables de Zoom ---
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

# --- Variables de YouTube ---
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Directorio por defecto de descargas (puede ser override en CLI)
def get_download_dir() -> Path:
    return Path(os.getenv("RECORDINGS_BASE_PATH", Path.home() / "Downloads" / "zoom2yt"))

FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
