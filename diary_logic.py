import json
import os
import uuid
import io # Para manejar la imagen del doodle como bytes

DATA_PATH = "data/diary.json"
IMAGES_DIR = "data/images"

def load_diary():
    if not os.path.exists(DATA_PATH):
        return []
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError: # Manejo de error si el JSON está vacío o corrupto
            return []

# Cambiamos la firma de la función para aceptar dos imágenes
def save_entry(date, location, text, memory_image_file=None, doodle_image_file=None):
    diary = load_diary()
    
    new_entry = {
        "id": str(uuid.uuid4()),
        "date": date,
        "location": location,
        "text": text,
        "memory_image_path": None, # Nueva clave para la foto de recuerdo
        "doodle_image_path": None  # Nueva clave para el doodle
    }

    # Procesar y guardar la foto de recuerdo
    if memory_image_file is not None:
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)

        memory_filename = f"memory_{location}_{uuid.uuid4()}.png".replace(" ", "_")
        memory_file_path = os.path.join(IMAGES_DIR, memory_filename)
        memory_image_file.save(memory_file_path, "PNG")
        new_entry["memory_image_path"] = memory_file_path

    # Procesar y guardar el doodle
    if doodle_image_file is not None:
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
        
        doodle_filename = f"doodle_{location}_{uuid.uuid4()}.png".replace(" ", "_")
        doodle_file_path = os.path.join(IMAGES_DIR, doodle_filename)
        # Asegurarse de que el doodle sea guardable como PNG
        doodle_image_file.save(doodle_file_path, "PNG") # Asumimos que doodle_image_file ya es un objeto PIL
        new_entry["doodle_image_path"] = doodle_file_path


    diary.append(new_entry)

    directory = os.path.dirname(DATA_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=4)

def get_entries():
    return load_diary()
