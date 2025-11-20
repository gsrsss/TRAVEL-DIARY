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
final_image_to_save = None 

if uploaded_file:
    # 1. Abrimos la imagen original
    image = Image.open(uploaded_file).convert("RGBA")
    
    # 2. Ajuste inteligente de tamaño para pantalla
    # Si la foto es gigante (mayor a 800px), la reducimos solo para el editor
    # (Esto arregla el problema de que la foto no se vea de fondo)
    max_width = 800
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        display_image = image.resize((max_width, new_height))
    else:
        display_image = image

    # 3. Controles de Dibujo (Color y Tamaño)
    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        stroke_color = st.color_picker("🎨 Color del pincel:", "#FF0000")
    with col_draw2:
        stroke_width = st.slider("✏️ Grosor del pincel:", 1, 25, 5)

    st.write("¡Dibuja o marca tu ruta encima de la foto!")
    
    # 4. El componente Lienzo (Canvas)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,  # Usamos el valor del slider
        stroke_color=stroke_color,  # Usamos el valor del color picker
        background_image=display_image, # Usamos la imagen ajustada
        update_streamlit=True,
        height=display_image.height, # Altura exacta de la imagen
        width=display_image.width,   # Ancho exacto de la imagen
        drawing_mode="freedraw",
        key="canvas",
    )

    # 5. Lógica para guardar (Fusionar dibujo con imagen ORIGINAL)
    if canvas_result.image_data is not None:
        # Obtenemos el dibujo
        drawing_data = canvas_result.image_data.astype("uint8")
        drawing_image = Image.fromarray(drawing_data, "RGBA")
        
        # Si usamos la imagen reducida para mostrar, aquí estiramos el dibujo
        # para que coincida con la foto original de alta calidad
        if drawing_image.size != image.size:
            drawing_image = drawing_image.resize(image.size, resample=Image.NEAREST)
            
        # Fusionamos
        combined_image = Image.alpha_composite(image, drawing_image)
        final_image_to_save = combined_image

# --- BOTÓN DE GUARDAR ---
if st.button("Guardar entrada"):
    if location and notes:
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
for e in reversed(entries):
    with st.expander(f"{e['date']} — {e['location']}"):
        st.write(e["text"])
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
