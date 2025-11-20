import json
import os
import uuid
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
DATA_PATH = "data/diary.json"
IMAGES_DIR = "data/images"

# Configurar cliente de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- VARIABLE GLOBAL CON EL MODELO NUEVO ---
# Este es el cambio clave: Usamos el modelo más reciente
CURRENT_MODEL = "llama-3.3-70b-versatile" 

# --- FUNCIONES DE BASE DE DATOS ---

def load_diary():
    if not os.path.exists(DATA_PATH): return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def _save_image(image_obj, prefix, location):
    if not image_obj: return None
    if not os.path.exists(IMAGES_DIR): os.makedirs(IMAGES_DIR)
    filename = f"{prefix}_{location}_{uuid.uuid4().hex[:8]}.png".replace(" ", "_")
    path = os.path.join(IMAGES_DIR, filename)
    image_obj.save(path, "PNG")
    return path

def save_entry(date, location, text, mem_img=None, doo_img=None, mem_title="", keyword=""):
    diary = load_diary()
    
    entry = {
        "id": str(uuid.uuid4()),
        "date": str(date),
        "location": location,
        "text": text,
        "keyword": keyword,
        "memory_title": mem_title,
        "memory_path": _save_image(mem_img, "mem", location),
        "doodle_path": _save_image(doo_img, "doo", location)
    }
    
    diary.append(entry)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=4)

def get_entries(): return load_diary()

# --- FUNCIONES DE IA (ACTUALIZADAS CON EL NUEVO MODELO) ---

def generate_story(location, notes):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un escritor de viajes poético. Escribe un párrafo corto y bonito estilo diario."},
                {"role": "user", "content": f"Lugar: {location}. Notas: {notes}"}
            ],
            model=CURRENT_MODEL, # <--- MODELO ACTUALIZADO
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"La IA está descansando... ({str(e)})"

def get_recommendations(place):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un experto en viajes 'aesthetic'. Da 3 recomendaciones cortas y únicas con emojis."},
                {"role": "user", "content": f"Recomiéndame qué hacer en {place}"}
            ],
            model=CURRENT_MODEL, # <--- MODELO ACTUALIZADO
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"No encontré recomendaciones... ({str(e)})"

def analyze_emotion(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Analiza el texto y responde con UNA SOLA palabra en español que describa la emoción principal (Ej: Alegría, Calma, Magia)."},
                {"role": "user", "content": text}
            ],
            model=CURRENT_MODEL, # <--- MODELO ACTUALIZADO
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content.strip()
    except:
        return "Viaje ✨"
