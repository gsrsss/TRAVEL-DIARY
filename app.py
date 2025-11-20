import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Importaciones locales
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
    # 1. Cargar imagen
    original_image = Image.open(uploaded_file)
    
    # 2. Ajustar imagen para pantalla (Max 700px)
    # Esto es crucial para que no se desborde la memoria del navegador
    max_width = 700
    if original_image.width > max_width:
        ratio = max_width / original_image.width
        new_height = int(original_image.height * ratio)
        # Usamos RGBA para asegurar compatibilidad con el canvas
        canvas_image = original_image.resize((max_width, new_height)).convert("RGBA")
    else:
        canvas_image = original_image.convert("RGBA")

    # --- DEBUG VISUAL ---
    # Esto te muestra que la imagen SÍ se cargó en memoria.
    # Si ves esta imagen pequeña pero no la grande de abajo, es un tema del navegador.
    st.caption("Vista previa de la imagen cargada:")
    st.image(canvas_image, width=150) 
    # --------------------

    # 3. Controles de Dibujo
    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        stroke_color = st.color_picker("🎨 Color del pincel:", "#FF0000")
    with col_draw2:
        stroke_width = st.slider("✏️ Grosor del pincel:", 1, 25, 5)

    st.write("👇 ¡Dibuja aquí abajo!")

    # 4. EL LIENZO (CANVAS)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)", 
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#eeeeee", # Fondo GRIS para ver si el canvas carga
        background_image=canvas_image, # La imagen procesada
        update_streamlit=True,
        height=canvas_image.height,
        width=canvas_image.width,
        drawing_mode="freedraw",
        key=f"canvas_{uploaded_file.name}", # Llave única para forzar recarga
    )

    # 5. PROCESAR GUARDADO
    if canvas_result.image_data is not None:
        # Recuperamos el dibujo
        drawing_data = canvas_result.image_data.astype("uint8")
        drawing_image = Image.fromarray(drawing_data, "RGBA")
        
        # Ajustamos el dibujo al tamaño de la imagen ORIGINAL
        if drawing_image.size != original_image.size:
            drawing_image = drawing_image.resize(original_image.size, resample=Image.NEAREST)
        
        # Preparamos la original para fusionar
        if original_image.mode != "RGBA":
            base_for_merge = original_image.convert("RGBA")
        else:
            base_for_merge = original_image
            
        # Fusionamos
        final_image_to_save = Image.alpha_composite(base_for_merge, drawing_image)

# --- BOTÓN DE GUARDAR ---
if st.button("Guardar entrada"):
    if location and notes:
        # Si no se dibujó nada pero hay foto, guardamos la foto original
        if final_image_to_save is None and uploaded_file:
            final_image_to_save = original_image
            
        save_entry(str(date), location, notes, final_image_to_save)
        st.success("¡Entrada guardada!")
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
