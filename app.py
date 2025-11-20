import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Importaciones locales (asumiendo que existen en tu carpeta)
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

# Inicializamos variables en el estado si no existen
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'original_upload_name' not in st.session_state:
    st.session_state.original_upload_name = None
if 'base_original' not in st.session_state:
    st.session_state.base_original = None

# Lógica de procesamiento de imagen (SOLO si cambia el archivo)
if uploaded_file:
    # Si es un archivo nuevo o diferente al anterior
    if st.session_state.original_upload_name != uploaded_file.name:
        
        # 1. CRUCIAL: Resetear el puntero del archivo al inicio
        uploaded_file.seek(0)
        
        original_image = Image.open(uploaded_file)
        
        # Guardamos una copia del original para guardar si no se dibuja
        st.session_state.base_original = original_image.copy()
        
        # 2. Ajustar imagen (Tu lógica original)
        max_width = 600
        if original_image.width > max_width:
            ratio = max_width / original_image.width
            new_height = int(original_image.height * ratio)
            resized_image = original_image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        else:
            resized_image = original_image.copy()

        # 3. Sanitización (Tu lógica original)
        canvas_bg = Image.new("RGB", resized_image.size, (255, 255, 255))
        if resized_image.mode in ('RGBA', 'LA'):
            canvas_bg.paste(resized_image, mask=resized_image.split()[-1])
        else:
            canvas_bg.paste(resized_image)
        
        # Guardamos en Session State
        st.session_state.processed_image = canvas_bg
        st.session_state.original_upload_name = uploaded_file.name

# Si el usuario quita el archivo, limpiamos el estado
elif not uploaded_file:
    st.session_state.processed_image = None
    st.session_state.base_original = None
    st.session_state.original_upload_name = None

# --- RENDERIZADO DEL CANVAS ---
final_image_to_save = None 

if st.session_state.processed_image:
    # 4. Controles de Dibujo
    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        stroke_color = st.color_picker("🎨 Color del pincel:", "#FF0000")
    with col_draw2:
        stroke_width = st.slider("✏️ Grosor del pincel:", 1, 25, 5)

    st.write("👇 ¡Dibuja aquí abajo!")

    # 5. EL LIENZO
    # Usamos la imagen almacenada en session_state
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        background_image=st.session_state.processed_image, # <--- CLAVE: Usar la del estado
        update_streamlit=True,
        height=st.session_state.processed_image.height,
        width=st.session_state.processed_image.width,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.original_upload_name}", 
    )

    # 6. PROCESAR GUARDADO (Combinar dibujo con original)
    if canvas_result.image_data is not None:
        # Detectar si realmente se dibujó algo (opcional, pero útil)
        # Aquí asumimos que si hay image_data, procesamos
        drawing_data = canvas_result.image_data.astype("uint8")
        drawing_image = Image.fromarray(drawing_data, "RGBA")
        
        # Recuperamos la original del estado para redimensionar el dibujo a su tamaño real
        original_ref = st.session_state.base_original
        
        if drawing_image.size != original_ref.size:
            drawing_image = drawing_image.resize(original_ref.size, resample=Image.NEAREST)
        
        if original_ref.mode != "RGBA":
            base_for_merge = original_ref.convert("RGBA")
        else:
            base_for_merge = original_ref
            
        final_image_to_save = Image.alpha_composite(base_for_merge, drawing_image)
else:
    st.info("Sube una imagen para habilitar el dibujo.")

# --- BOTÓN DE GUARDAR ---
if st.button("Guardar entrada"):
    if location and notes:
        # Si no hay dibujo final pero sí hay imagen original cargada, usamos la original
        if final_image_to_save is None and st.session_state.base_original is not None:
            final_image_to_save = st.session_state.base_original
            
        save_entry(str(date), location, notes, final_image_to_save)
        st.success("¡Entrada guardada con éxito!")
        # Opcional: Limpiar estado tras guardar
        # st.session_state.processed_image = None
        # st.experimental_rerun()
    else:
        st.warning("Por favor escribe al menos el lugar y las notas.")

# --- SECCIÓN IA ---
if st.button("✨ Generar relato con IA"):
    if location and notes:
        with st.spinner("La IA está escribiendo tu historia..."):
            try:
                story = generate_story(location, notes)
                st.write("### 📝 Relato generado")
                st.write(story)
            except Exception as e:
                st.error(f"Error con la IA: {e}")
    else:
        st.error("Debes ingresar lugar y notas.")

# --- SECCIÓN 2: VER TU DIARIO ---
st.header("📚 Tu diario")
st.divider()

entries = get_entries()
for e in reversed(entries):
    with st.expander(f"{e['date']} — {e['location']}"):
        st.write(e["text"])
        if e.get("image_path"):
            try:
                st.image(e["image_path"], caption="Recuerdo guardado")
            except:
                st.write("🖼️ (Imagen no encontrada)")

# --- SECCIÓN 3: RECOMENDACIONES ---
st.header("🌍 Recomendaciones")
place = st.text_input("¿A dónde quieres ir ahora?")
if st.button("Ver recomendaciones"):
    if place:
        with st.spinner("Buscando destinos..."):
            try:
                recs = get_recommendations(place)
                st.write(recs)
            except Exception as e:
                st.error(f"Error trayendo recomendaciones: {e}")
