import os
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../../config"))

ENV_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "../../config/.env"))
load_dotenv(dotenv_path=ENV_PATH)

RECORDINGS_BASE_PATH = os.getenv("RECORDINGS_BASE_PATH")
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

LOGS_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../../logs"))
DATA_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../../data"))
OUTPUT_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../../output"))

LOG_FILE = os.path.join(LOGS_DIR, "last_uploaded.log")
IFRAME_JSON_FILE = os.path.join(DATA_DIR, "iframes.json")
HTML_FILE = os.path.join(OUTPUT_DIR, "iframes_clean.html")


YOUTUBE_CLIENT_SECRETS = os.path.join(CONFIG_DIR, "client_secret.json")
YOUTUBE_TOKEN_FILE = os.path.join(CONFIG_DIR, "token.pickle")

VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]