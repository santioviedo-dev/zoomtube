import json
from ..utils.config import IFRAME_JSON_FILE

def save_iframe_json(videos_id: list, data=[]):
    for video_id in videos_id:
        iframe = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen=""></iframe>'
        data.append({"iframe": iframe})
        
    with open(IFRAME_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        

def load_iframe_json():
    data = []
    with open(IFRAME_JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def clean_iframe_json():
    with open(IFRAME_JSON_FILE, "w", encoding="utf-8") as f:
        f.write("")