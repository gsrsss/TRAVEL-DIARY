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

# --- SECCIÓN 2: FOTO DE RECUERDO + STAMPS ---
st.subheader("📸 Sube una foto y decórala")

# 1. Subida de imagen
uploaded_memory_photo = st.file_uploader("Elige una imagen:", type=["png", "jpg", "jpeg"], key="memory_photo_uploader")
memory_title = st.text_input("Título de la foto:", placeholder="Ej. Comiendo Dango en Tokio 🍡")

# Inicializar estado de la imagen
if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

# Cargar imagen nueva
if uploaded_memory_photo:
    # Solo cargamos si es diferente a lo que ya tenemos (para no perder los stamps al recargar)
    # Un truco simple es verificar si memory_image es None, o forzar recarga si el usuario cambia el archivo
    uploaded_memory_photo.seek(0)
    # Solo sobrescribimos si NO tenemos imagen o si el usuario acaba de subir una (esto requiere lógica de ID, 
    # pero para simplificar: si subes archivo, se resetea la imagen base)
    if st.session_state.memory_image is None: 
         st.session_state.memory_image = Image.open(uploaded_memory_photo)

# 2. Herramienta de Stamps (Solo aparece si hay foto)
if st.session_state.memory_image:
    
    # Mostrar la imagen actual
    st.image(st.session_state.memory_image, caption=memory_title if memory_title else "Tu Recuerdo", use_column_width=True)

    with st.expander("✨ Herramienta de Stamps (Decorar foto)"):
        st.write("Elige un emoji y colócalo sobre la foto:")
        
        # Controles de Stamp
        c_stamp1, c_stamp2 = st.columns(2)
        
        with c_stamp1:
            # Lista de Emojis "Cute"
            emoji_list = ["📍", "✈️", "🍡", "🌸", "❤️", "😊", "📸", "🍜", "⛩️", "✨", "🐱", "🍵"]
            selected_emoji = st.selectbox("Elige un Stamp:", emoji_list)
            stamp_color = st.color_picker("Color del Stamp:", "#FF69B4") # Rosa por defecto
            
        with c_stamp2:
            stamp_size = st.slider("Tamaño:", 20, 200, 80)
            
        # Posicionamiento (Porcentajes para que funcione en cualquier tamaño de foto)
        col_pos1, col_pos2 = st.columns(2)
        x_pos_pct = col_pos1.slider("Posición Horizontal (X)", 0, 100, 50)
        y_pos_pct = col_pos2.slider("Posición Vertical (Y)", 0, 100, 50)

        if st.button("Poner Sello ✅"):
            # Lógica para "pintar" el emoji en la imagen
            img_copy = st.session_state.memory_image.copy().convert("RGBA")
            draw = ImageDraw.Draw(img_copy)
            
            # Intentar cargar fuente (Arial suele tener emojis simples, o default)
            try:
                # Intentamos cargar una fuente del sistema grande
                font = ImageFont.truetype("arial.ttf", stamp_size)
            except:
                font = ImageFont.load_default()
            
            # Calcular posición en pixeles reales
            img_w, img_h = img_copy.size
            x_px = int((x_pos_pct / 100) * img_w)
            y_px = int((y_pos_pct / 100) * img_h)
            
            # Centrar el emoji en el punto (x,y)
            # Nota: textsize es antiguo, usamos una aproximación o textbbox si es python nuevo, 
            # pero para compatibilidad simple dibujamos centrado en el ancla 'mm' (middle-middle)
            try:
                draw.text((x_px, y_px), selected_emoji, font=font, fill=stamp_color, anchor="mm")
            except ValueError:
                # Si la version de Pillow es vieja y no soporta anchor, usamos cálculo manual simple
                draw.text((x_px, y_px), selected_emoji, font=font, fill=stamp_color)

            # Actualizar la imagen en el estado
            st.session_state.memory_image = img_copy
            st.success("¡Stamp agregado! (Puedes agregar más)")
            st.experimental_rerun() # Recargar para ver el cambio inmediatamente

    if st.button("🗑️ Borrar cambios (Resetear foto)"):
        st.session_state.memory_image = None
        st.experimental_rerun()

else:
    st.info("Sube una foto para empezar a decorarla.")


# --- SECCIÓN 3: DOODLE SPACE ---
st.subheader("🎨 Doodle Space: Ilustra las vibras")
st.write("Dibuja aquí algo abstracto o divertido que represente cómo te sentiste.")

cd1, cd2, cd3 = st.columns(3)
doodle_bg = cd1.color_picker("Fondo", "#F0F2F6")
brush_col = cd2.color_picker("Pincel", "#000000")
brush_sz = cd3.slider("Grosor", 1, 10, 3)

doodle_res = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=brush_sz,
    stroke_color=brush_col,
    background_color=doodle_bg,
    background_image=None, # Mantenemos esto limpio
    update_streamlit=True,
    height=400,
    width=700,
    drawing_mode="freedraw",
    key="doodle_cv",
)

# --- GUARDAR ---
if st.button("💾 Guardar entrada", type="primary"):
    if location and notes:
        # 1. Imagen de recuerdo (ya tiene los stamps integrados)
        mem_img = st.session_state.memory_image
        
        # 2. Doodle
        doo_img = None
        if doodle_res.image_data is not None:
            # Procesar transparencia del doodle
            raw_doodle = Image.fromarray(doodle_res.image_data.astype("uint8"), "RGBA")
            bg = Image.new("RGBA", raw_doodle.size, tuple(int(doodle_bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,))
            doo_img = Image.alpha_composite(bg, raw_doodle)
            
            # Convertir a bytes para guardar
            buf = io.BytesIO()
            doo_img.save(buf, format="PNG")
            buf.seek(0)
            doo_img = Image.open(buf)

        save_entry(str(date), location, notes, mem_img, doo_img, memory_title)
        st.success("¡Guardado!")
        st.session_state.memory_image = None
    else:
        st.warning("Faltan datos.")

# --- IA & EXTRAS ---
if st.button("✨ Generar relato IA"):
    if location and notes:
        with st.spinner("Escribiendo..."):
            st.write(generate_story(location, notes))

st.divider()
st.header("📚 Historial")
for e in reversed(get_entries()):
    with st.expander(f"{e['date']} - {e['location']}"):
        st.write(e['text'])
        c1, c2 = st.columns(2)
        if e.get('memory_path'): 
            t = e.get('memory_title') or "Recuerdo"
            c1.image(e['memory_path'], caption=t)
        if e.get('doodle_path'): c2.image(e['doodle_path'], caption="Vibes")

st.header("🌍 Recomendaciones")
dest = st.text_input("¿Próximo destino?")
if st.button("Buscar") and dest:
    st.write(get_recommendations(dest))
