import json
import os
import uuid

DATA_PATH = "data/diary.json"
IMAGES_DIR = "data/images"

def load_diary():
    if not os.path.exists(DATA_PATH): return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def _save_image(image_obj, prefix, location):
    """Función auxiliar para guardar imágenes y retornar la ruta."""
    if not image_obj: return None
    if not os.path.exists(IMAGES_DIR): os.makedirs(IMAGES_DIR)
    
    filename = f"{prefix}_{location}_{uuid.uuid4().hex[:8]}.png".replace(" ", "_")
    path = os.path.join(IMAGES_DIR, filename)
    image_obj.save(path, "PNG")
    return path

def save_entry(date, location, text, memory_img=None, doodle_img=None):
    diary = load_diary()
    
    entry = {
        "id": str(uuid.uuid4()),
        "date": str(date),
        "location": location,
        "text": text,
        "memory_path": _save_image(memory_img, "mem", location),
        "doodle_path": _save_image(doodle_img, "doo", location)
    }
    
    diary.append(entry)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=4)

def get_entries(): return load_diary()
