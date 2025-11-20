import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io 

# Importaciones locales
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

# --- Configuración de la página ---
st.set_page_config(layout="wide") 
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

# --- SECCIÓN DE FOTO DE RECUERDO ---
st.subheader("📸 Sube una foto como recuerdo")
uploaded_memory_photo = st.file_uploader("Elige una imagen para tu recuerdo:", type=["png", "jpg", "jpeg"], key="memory_photo_uploader")

# INPUT PARA EL TÍTULO DEL RECUERDO
memory_title = st.text_input("Título de este recuerdo (Opcional):", placeholder="Ej. Atardecer en la playa")

# Almacenamos la imagen del recuerdo en session_state
if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

if uploaded_memory_photo:
    uploaded_memory_photo.seek(0) 
    st.session_state.memory_image = Image.open(uploaded_memory_photo)
    # Mostramos la imagen
    caption_text = memory_title if memory_title else "Vista previa del recuerdo"
    st.image(st.session_state.memory_image, caption=caption_text, use_column_width=True)
else:
    st.session_state.memory_image = None 

# --- SECCIÓN DE DOODLE SPACE ---
st.subheader("🎨 Doodle Space: Ilustra las vibras de tu viaje")

col_doodle_controls_1, col_doodle_controls_2, col_doodle_controls_3 = st.columns(3)

with col_doodle_controls_1:
    doodle_bg_color = st.color_picker("Color de fondo:", "#F0F2F6") 
with col_doodle_controls_2:
    doodle_stroke_color = st.color_picker("Pincel:", "#000000")
with col_doodle_controls_3:
    doodle_stroke_width = st.slider("Grosor:", 1, 10, 3)

doodle_width = 700
doodle_height = 400

st.write("👇 ¡Dibuja aquí abajo!")

# Canvas
doodle_canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)", 
    stroke_width=doodle_stroke_width,
    stroke_color=doodle_stroke_color,
    background_color=doodle_bg_color, 
    background_image=None, # Importante para que se vea el color de fondo
    update_streamlit=True,
    height=doodle_height,
    width=doodle_width,
    drawing_mode="freedraw", 
    key="doodle_canvas",
)

# Inicializamos el resultado final del doodle
doodle_final_image_to_save = None

# Procesar el dibujo para guardar
if doodle_canvas_result.image_data is not None:
    # 1. Obtener el dibujo (con fondo transparente)
    doodle_image = Image.fromarray(doodle_canvas_result.image_data.astype("uint8"), "RGBA")
    
    # 2. Crear una imagen sólida con el color de fondo elegido
    # (Esto es necesario porque el canvas devuelve fondo transparente en image_data)
    bg_rgb = tuple(int(doodle_bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    solid_bg = Image.new("RGBA", doodle_image.size, bg_rgb + (255,))
    
    # 3. Fusionar: Fondo de color + Dibujo
    doodle_final_image_to_save = Image.alpha_composite(solid_bg, doodle_image)


# --- BOTÓN DE GUARDAR ---
if st.button("💾 Guardar entrada", type="primary"):
    if location and notes:
        memory_image_to_save = st.session_state.memory_image

        doodle_to_save = None
        if doodle_final_image_to_save:
            doodle_bytes_io = io.BytesIO()
            doodle_final_image_to_save.save(doodle_bytes_io, format="PNG")
            doodle_bytes_io.seek(0)
            doodle_to_save = Image.open(doodle_bytes_io) 
            
        save_entry(str(date), location, notes, memory_image_to_save, doodle_to_save, memory_title)
        
        st.success("¡Entrada guardada!")
        st.session_state.memory_image = None
    else:
        st.warning("Por favor, ingresa al menos el lugar y las notas.")

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
        
        col_ver1, col_ver2 = st.columns(2)
        
        with col_ver1:
            if e.get("memory_path"): 
                titulo_foto = e.get("memory_title") if e.get("memory_title") else "Recuerdo"
                try:
                    st.image(e["memory_path"], caption=titulo_foto, use_column_width=True)
                except:
                    st.write("🖼️ (Imagen no disponible)")
        
        with col_ver2:
            if e.get("doodle_path"): 
                try:
                    st.image(e["doodle_path"], caption="Vibes / Doodle", use_column_width=True)
                except:
                    st.write("🎨 (Doodle no disponible)")

# --- SECCIÓN 3: RECOMENDACIONES ---
st.header("🌍 Recomendaciones")
place = st.text_input("¿A dónde quieres ir ahora?")
if st.
