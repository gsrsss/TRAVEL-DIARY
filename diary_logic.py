import json
import os

DATA_PATH = "data/diary.json"

def load_diary():
    # Si el archivo no existe, retornamos una lista vacía
    if not os.path.exists(DATA_PATH):
        return []
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_entry(date, location, text):
    diary = load_diary()
    new_entry = {
        "date": date,
        "location": location,
        "text": text
    }
    diary.append(new_entry)

    # --- CORRECCIÓN AQUÍ ---
    # Obtenemos el nombre de la carpeta ("data")
    directory = os.path.dirname(DATA_PATH)
    
    # Si la carpeta tiene nombre y no existe, la creamos
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    # -----------------------

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=4)

def get_entries():
    return load_diary()
