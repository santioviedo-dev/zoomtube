import re
import os
import json
from .config import LOG_FILE, IFRAME_JSON_FILE

def sanitize_filename(name):
    """
    Removes invalid characters from file names for common file systems.
    """
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.strip()

def load_uploaded_log():
    return set(open(LOG_FILE, "r", encoding="utf-8").read().splitlines()) if os.path.exists(LOG_FILE) else set()

def record_uploaded_video(file_path):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a+', encoding='utf-8') as f:
        f.seek(0)
        contenido = f.read()
    
        if file_path not in contenido:
            f.write(file_path + '\n')
        

