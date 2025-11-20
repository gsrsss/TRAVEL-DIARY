import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas

# Importaciones locales (Tus archivos originales)
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

st.set_page_config(page_title="Travel Diary", layout="wide")
st.title("📘 Travel Diary – Diario de Viajes IA")
st.write("Guarda tus experiencias, fotos y recuerdos. La IA te ayuda a escribirlas.")

# Inicializar estado de sesión para la foto de recuerdo
if 'mem_img' not in st.session_state:
    st.session_state.mem_img = None

# --- SECCIÓN 1: CREAR ENTRADA ---
st.header("✍️ Agregar nuevo recuerdo")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Fecha del viaje")
with col2:
    location = st.text_input("Lugar visitado")

notes = st.text_area("Escribe tus notas o experiencias")

# --- SECCIÓN 2: FOTO DE RECUERDO (Solo visualización) ---
st.subheader("📸 Sube una foto como recuerdo")
uploaded_file = st.file_uploader("Elige una imagen:", type=["png", "jpg", "jpeg"], key="mem_uploader")

# Input para el nombre único de la foto
memory_title = st.text_input("Título de este recuerdo (Opcional)", placeholder="Ej. Atardecer increíble")

if uploaded_file:
    uploaded_file.seek(0) # Resetear puntero por seguridad
    st.session_state.mem_img = Image.open(uploaded_file)

# Mostrar la imagen si está cargada
if st.session_state.mem_img:
    st.image(st.session_state.mem_img, caption=memory_title if memory_title else "Foto de recuerdo", use_column_width=True)


# --- SECCIÓN 3: DOODLE SPACE (Vibras del viaje) ---
st.subheader("🎨 Doodle Space: Ilustra las vibras")
st.write("Dibuja y añade texto para capturar la esencia del viaje.")

# Controles del Doodle
dc1, dc2, dc3 = st.columns(3)
with dc1:
    doodle_bg = st.color_picker("Fondo del Doodle", "#F0F2F6")
with dc2:
    brush_color = st.color_picker("Color Pincel", "#000000")
with dc3:
    stroke_width = st.slider("Grosor Pincel", 1, 20, 3)

# Herramienta de Texto sobre el Doodle
with st.expander("🔤 Herramienta de Texto (Escribir sobre el dibujo)"):
    tc1, tc2, tc3 = st.columns([3, 1, 1])
    text_input = tc1.text_input("Texto a añadir")
    text_color = tc2.color_picker("Color Texto", "#FF0000")
    text_size = tc3.number_input("Tamaño Fuente", 10, 100, 20)

# El Canvas
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=stroke_width,
    stroke_color=brush_color,
    background_color=doodle_bg,
    height=400,
    width=700,
    drawing_mode="freedraw",
    key="doodle_canvas",
)

# --- BOTÓN GUARDAR ---
if st.button("💾 Guardar Entrada", type="primary"):
    if location and notes:
        final_doodle = None
        
        # Procesar el dibujo del canvas
        if canvas_result.image_data is not None:
            # Convertir numpy array a imagen PIL
            img_doodle = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
            
            # Si el usuario escribió texto, lo pegamos encima
            if text_input:
                # Crear un lienzo base del color del fondo para manejar transparencias correctamente
                bg_rgb = tuple(int(doodle_bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                base_img = Image.new("RGBA", img_doodle.size, bg_rgb + (255,))
                
                draw = ImageDraw.Draw(base_img)
                # Intentar cargar fuente, si falla usar default
                try:
                    font = ImageFont.truetype("arial.ttf", text_size)
                except:
                    font = ImageFont.load_default()
                
                # Centrar texto (calculo simple)
                w_text, h_text = draw.textsize(text_input, font=font) if hasattr(draw, 'textsize') else (0,0)
                x_pos = (img_doodle.width - w_text) / 2
                y_pos = (img_doodle.height - h_text) / 2
                
                draw.text((x_pos, y_pos), text_input, font=font, fill=text_color)
                
                # Combinar texto + dibujo
                final_doodle = Image.alpha_composite(base_img, img_doodle)
            else:
                final_doodle = img_doodle

        # Guardar todo usando la lógica
        save_entry(date, location, notes, st.session_state.mem_img, final_doodle, memory_title)
        st.success("¡Entrada guardada con éxito!")
        
        # Limpiar estado de la foto (opcional)
        st.session_state.mem_img = None
    else:
        st.warning("Por favor escribe al menos el lugar y las notas.")


# --- SECCIÓN 4: GENERAR RELATO CON IA (RESTAURADO) ---
st.divider()
if st.button("✨ Generar relato con IA"):
    if location and notes:
        with st.spinner("La IA está escribiendo tu historia..."):
            try:
                story = generate_story(location, notes)
                st.write("### 📝 Relato generado")
                st.markdown(story)
            except Exception as e:
                st.error(f"Error generando historia: {e}")
    else:
        st.error("Debes ingresar lugar y notas para generar la historia.")


# --- SECCIÓN 5: VER TU DIARIO (HISTORIAL) ---
st.header("📚 Tu diario")
entries = get_entries()

for e in reversed(entries):
    with st.expander(f"{e['date']} — {e['location']}"):
        st.write(e["text"])
        
        col_h1, col_h2 = st.columns(2)
        
        # Mostrar Foto de Recuerdo
        with col_h1:
            if e.get("memory_path"):
                title_show = e.get("memory_title") if e.get("memory_title") else "Recuerdo"
                try:
                    st.image(e["memory_path"], caption=title_show, use_column_width=True)
                except:
                    st.error("Error cargando imagen")
        
        # Mostrar Doodle
        with col_h2:
            if e.get("doodle_path"):
                try:
                    st.image(e["doodle_path"], caption="Vibes / Doodle", use_column_width=True)
                except:
                    st.error("Error cargando doodle")


# --- SECCIÓN 6: RECOMENDACIONES (RESTAURADO) ---
st.divider()
st.header("🌍 Recomendaciones")
place_input = st.text_input("¿A dónde quieres ir ahora?")

if st.button("Ver recomendaciones"):
    if place_input:
        with st.spinner("Buscando los mejores lugares..."):
            try:
                recs = get_recommendations(place_input)
                st.write("### Lugares recomendados:")
                st.write(recs)
            except Exception as e:
                st.error(f"Error obteniendo recomendaciones: {e}")
