import streamlit as st
from PIL import Image, ImageDraw, ImageFont 
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

# --- NUEVO: INPUT PARA EL TÍTULO DEL RECUERDO ---
memory_title = st.text_input("Título de este recuerdo (Opcional):", placeholder="Ej. Atardecer en la playa")

# Almacenamos la imagen del recuerdo en session_state
if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

if uploaded_memory_photo:
    uploaded_memory_photo.seek(0) 
    st.session_state.memory_image = Image.open(uploaded_memory_photo)
    # Mostramos la imagen con el título que escriba el usuario
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

# Herramienta de texto
st.markdown("---")
st.markdown("### 📝 Añadir Texto al Doodle")
text_to_add = st.text_input("Escribe el texto que quieres añadir:")
col_txt1, col_txt2, col_txt3 = st.columns(3)
with col_txt1:
    text_color = st.color_picker("Color texto:", "#FF0000")
with col_txt2:
    font_size = st.slider("Tamaño:", 10, 80, 30)
with col_txt3:
    font_family = st.selectbox("Fuente:", ["Arial", "Courier New", "Verdana", "Times New Roman"], index=0)

# --- ARREGLO DEL CANVAS ---
st.write("👇 ¡Dibuja aquí abajo!")

# Nota: He añadido background_image=None explícitamente para evitar conflictos
doodle_canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)", 
    stroke_width=doodle_stroke_width,
    stroke_color=doodle_stroke_color,
    background_color=doodle_bg_color, 
    background_image=None, # <--- ESTO ES IMPORTANTE PARA QUE SE VEA EL FONDO DE COLOR
    update_streamlit=True,
    height=doodle_height,
    width=doodle_width,
    drawing_mode="freedraw", 
    key="doodle_canvas",
)

# Inicializamos el resultado final del doodle
doodle_final_image_to_save = None

# Procesar el doodle y añadir texto
if doodle_canvas_result.image_data is not None:
    # Convertir el resultado del canvas a una imagen PIL
    doodle_image = Image.fromarray(doodle_canvas_result.image_data.astype("uint8"), "RGBA")

    # Si hay texto para añadir
    if text_to_add:
        # Crear fondo base del color seleccionado
        bg_rgb = tuple(int(doodle_bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_base_image = Image.new("RGBA", doodle_image.size, bg_rgb + (255,)) 

        draw = ImageDraw.Draw(text_base_image)
        try:
            font = ImageFont.truetype(f"{font_family.lower()}.ttf", font_size)
        except IOError:
            font = ImageFont.load_default() 

        # Centrar texto
        # Nota: textsize está deprecado en versiones nuevas de Pillow, usamos textbbox si falla
        try:
             w_text, h_text = draw.textsize(text_to_add, font=font)
        except AttributeError:
             left, top, right, bottom = draw.textbbox((0, 0), text_to_add, font=font)
             w_text, h_text = right - left, bottom - top

        x = (doodle_image.width - w_text) / 2
        y = (doodle_image.height - h_text) / 2
        
        draw.text((x, y), text_to_add, font=font, fill=text_color)
        
        # Combinar el texto con el dibujo del usuario
        doodle_final_image_to_save = Image.alpha_composite(text_base_image, doodle_image)
    else:
        # Si no hay texto, usamos el doodle tal cual (pero asegurando el fondo de color)
        # Creamos una base solida con el color de fondo
        bg_rgb = tuple(int(doodle_bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        solid_bg = Image.new("RGBA", doodle_image.size, bg_rgb + (255,))
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
            
        # --- PASAMOS EL TÍTULO (memory_title) A LA FUNCIÓN ---
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
                # Recuperar el título, o usar "Recuerdo" por defecto
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
if st.button("Ver recomendaciones"):
    if place:
        with st.spinner("Buscando destinos..."):
            try:
                recs = get_recommendations(place)
                st.write(recs)
            except Exception as e:
                st.error(f"Error trayendo recomendaciones: {e}")
