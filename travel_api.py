import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_story(location, notes):
    prompt = f"Escribe un relato breve, cálido y bonito sobre un viaje a {location}. Estas fueron mis notas: {notes}"
    
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres un escritor experto en diarios de viaje."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def get_recommendations(place):
    prompt = f"Dame recomendaciones de viaje para visitar {place}. Incluye 3 actividades y consejos."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres un guía turístico experto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


