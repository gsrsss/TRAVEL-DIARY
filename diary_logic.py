import json
import os
import uuid # Para generar nombres únicos a las fotos

DATA_PATH = "data/diary.json"
IMAGES_DIR = "data/images" # Carpeta para las fotos

def load_diary():
    if not os.path.exists(DATA_PATH):
        return []
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_entry(date, location, text, image_file=None):
    diary = load_diary()
    
    new_entry = {
        "id": str(uuid.uuid4()),
        "date": date,
        "location": location,
        "text": text,
        "image_path": None # Por defecto sin foto
    }

    if image_file is not None:
        # 1. Crear carpeta de imágenes si no existe
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)

        filename = f"{location}_{uuid.uuid4()}.png".replace(" ", "_")
        file_path = os.path.join(IMAGES_DIR, filename)

        image_file.save(file_path, "PNG")
        
        new_entry["image_path"] = file_path

    diary.append(new_entry)

    directory = os.path.dirname(DATA_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=4)

def get_entries():
    return load_diary()
