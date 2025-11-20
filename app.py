import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas # Librería de dibujo

# Tus importaciones locales
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

st.title("📘 Travel Diary – Diario de Viajes IA")
st.write("Guarda tus experiencias, fotos y recuerdos. La IA te ayuda a escribirlas.")

# --- SECCIÓN 1: CREAR ENTRADA ---
st.header("✍️ Agregar nuevo recuerdo")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Fecha del viaje")
with col2:
    location = st.text_input("Lugar visitado")

notes = st.text_area("Escribe tus notas o experiencias")

# --- SECCIÓN DE FOTO Y DIBUJO ---
st.subheader("📸 Sube una foto y dibuja")
uploaded_file = st.file_uploader("Elige una imagen:", type=["png", "jpg", "jpeg"])
final_image_to_save = None # Variable para guardar la imagen final

if uploaded_file:
    # Abrimos la imagen original
    image = Image.open(uploaded_file).convert("RGBA")
    
    # Configuramos el lienzo de dibujo
    st.write("🎨 ¡Dibuja o marca tu ruta encima de la foto!")
    
    # El componente st_canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)", 
        stroke_width=5,
        stroke_color="#FF0000", # Color rojo por defecto
        background_image=image, # La foto subida es el fondo
        update_streamlit=True,
        height=400, # Altura del editor
        drawing_mode="freedraw",
        key="canvas",
    )

    # Lógica para combinar el dibujo con la foto original
    if canvas_result.image_data is not None:
        # Obtenemos los trazos del dibujo
        drawing_data = canvas_result.image_data.astype("uint8")
        drawing_image = Image.fromarray(drawing_data, "RGBA")
        
        # IMPORTANTE: Redimensionar el dibujo al tamaño de la foto original para que coincidan
        if drawing_image.size != image.size:
            drawing_image = drawing_image.resize(image.size)
            
        # Fusionar foto + dibujo
        combined_image = Image.alpha_composite(image, drawing_image)
        final_image_to_save = combined_image

# --- BOTÓN DE GUARDAR ---
if st.button("Guardar entrada"):
    if location and notes:
        # Llamamos a la nueva función save_entry que ahora acepta imagen
        save_entry(str(date), location, notes, final_image_to_save)
        st.success("¡Entrada guardada con foto y dibujo!")
    else:
        st.warning("Por favor escribe al menos el lugar y las notas.")

# --- SECCIÓN IA ---
if st.button("✨ Generar relato con IA"):
    if location and notes:
        with st.spinner("La IA está escribiendo tu historia..."):
            story = generate_story(location, notes)
            st.write("### 📝 Relato generado")
            st.write(story)
    else:
        st.error("Debes ingresar lugar y notas.")

# --- SECCIÓN 2: VER TU DIARIO ---
st.header("📚 Tu diario")

entries = get_entries()
# Mostramos las entradas más recientes primero (invertimos la lista)
for e in reversed(entries):
    with st.expander(f"{e['date']} — {e['location']}"):
        st.write(e["text"])
        
        # Si hay imagen guardada, la mostramos
        if e.get("image_path"):
            try:
                st.image(e["image_path"], caption="Recuerdo guardado")
            except:
                st.write("🖼️ (Imagen no disponible)")
        
        st.write("---")

# --- SECCIÓN 3: RECOMENDACIONES ---
st.header("🌍 Recomendaciones")
place = st.text_input("¿A dónde quieres ir ahora?")
if st.button("Ver recomendaciones"):
    if place:
        recs = get_recommendations(place)
        st.write(recs)
    if place:
        recs = get_recommendations(place)
        st.write(recs)

