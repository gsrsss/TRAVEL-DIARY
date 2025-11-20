import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import io 
import os

# Importaciones locales
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

# --- Configuración de la página ---
st.set_page_config(layout="wide") 
st.title("📘 Travel Diary – Diario de Viajes IA")
st.write("Guarda tus experiencias, fotos y recuerdos.")

# --- FUNCIÓN AUXILIAR PARA FUENTES ---
def get_font(size):
    """Intenta cargar una fuente del sistema que permita cambiar el tamaño."""
    font_names = ["arial.ttf", "Verdana.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "msyh.ttc"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    # Si falla todo, usa la default (pero avisamos que será pequeña)
    return ImageFont.load_default()

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

uploaded_memory_photo = st.file_uploader("Elige una imagen:", type=["png", "jpg", "jpeg"], key="memory_photo_uploader")
memory_title = st.text_input("Título de la foto:", placeholder="Ej. Comiendo Dango en Tokio 🍡")

if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

# Cargar imagen nueva
if uploaded_memory_photo:
    uploaded_memory_photo.seek(0)
    # Solo recargamos si no hay imagen en sesión (para no borrar stamps al interactuar)
    if st.session_state.memory_image is None: 
         st.session_state.memory_image = Image.open(uploaded_memory_photo)

if st.session_state.memory_image:
    
    # Mostramos la imagen actual
    st.image(st.session_state.memory_image, caption=memory_title if memory_title else "Tu Recuerdo", use_column_width=True)

    with st.expander("✨ Herramienta de Stamps (Decorar foto)", expanded=True):
        
        # Opción de Texto Personalizado o Símbolos
        mode = st.radio("Tipo de Sello:", ["Símbolos", "Texto Personalizado"], horizontal=True)
        
        c_stamp1, c_stamp2 = st.columns(2)
        
        text_to_stamp = ""
        
        with c_stamp1:
            if mode == "Símbolos":
                # Usamos símbolos unicode simples que funcionan en cualquier fuente
                emoji_list = ["★", "♥", "☺", "✈", "♫", "❄", "☀", "✿", "⚡", "⚓", "Recuerdo", "Viaje", "2025"]
                text_to_stamp = st.selectbox("Elige un Stamp:", emoji_list)
            else:
                text_to_stamp = st.text_input("Escribe tu texto:", "Tokio")
                
            stamp_color = st.color_picker("Color:", "#FF0055") 
            
        with c_stamp2:
            stamp_size = st.slider("Tamaño:", 20, 200, 100)
            
        # Posicionamiento
        st.write("Posición del sello:")
        col_pos1, col_pos2 = st.columns(2)
        x_pos_pct = col_pos1.slider("↔️ Izquierda - Derecha (%)", 0, 100, 50)
        y_pos_pct = col_pos2.slider("↕️ Arriba - Abajo (%)", 0, 100, 50)

        if st.button("✅ Estampar en la foto"):
            # Copia de trabajo
            img_copy = st.session_state.memory_image.copy().convert("RGBA")
            draw = ImageDraw.Draw(img_copy)
            
            # Cargar fuente robusta
            font = get_font(stamp_size)
            
            # Calcular posición
            img_w, img_h = img_copy.size
            x_px = int((x_pos_pct / 100) * img_w)
            y_px = int((y_pos_pct / 100) * img_h)
            
            # Dibujar texto centrado
            # Truco para centrar texto en versiones viejas de Pillow
            try:
                w_text, h_text = draw.textsize(text_to_stamp, font=font)
            except:
                # Fallback para versiones nuevas de Pillow (10+)
                left, top, right, bottom = draw.textbbox((0, 0), text_to_stamp, font=font)
                w_text, h_text = right - left, bottom - top
            
            final_x = x_px - (w_text / 2)
            final_y = y_px - (h_text / 2)

            draw.text((final_x, final_y), text_to_stamp, font=font, fill=stamp_color)

            # Guardar cambios
            st.session_state.memory_image = img_copy
            st.success("¡Stamp agregado!")
            st.experimental_rerun() 

    if st.button("🗑️ Borrar stamps (Resetear foto)"):
        st.session_state.memory_image = None
        st.experimental_rerun()

else:
    st.info("Sube una foto primero para usar los stamps.")


# --- SECCIÓN 3: DOODLE SPACE ---
st.subheader("🎨 Doodle Space: Ilustra las vibras")

cd1, cd2, cd3 = st.columns(3)
doodle_bg = cd1.color_picker("Fondo", "#F0F2F6")
brush_col = cd2.color_picker("Pincel", "#000000")
brush_sz = cd3.slider("Grosor", 1, 10, 3)

# Canvas limpio
doodle_res = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=brush_sz,
    stroke_color=brush_col,
    background_color=doodle_bg,
    background_image=None, 
    update_streamlit=True,
    height=400,
    width=700,
    drawing_mode="freedraw",
    key="doodle_cv",
)

# --- GUARDAR ---
if st.button("💾 Guardar entrada", type="primary"):
    if location and notes:
        # 1. Imagen de recuerdo
        mem_img = st.session_state.memory_image
        
        # 2. Doodle
        doo_img = None
        if doodle_res.image_data is not None:
            raw_doodle = Image.fromarray(doodle_res.image_data.astype("uint8"), "RGBA")
            # Crear fondo solido
            bg = Image.new("RGBA", raw_doodle.size, tuple(int(doodle_bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,))
            doo_img = Image.alpha_composite(bg, raw_doodle)
            
            buf = io.BytesIO()
            doo_img.save(buf, format="PNG")
            buf.seek(0)
            doo_img = Image.open(buf)

        save_entry(str(date), location, notes, mem_img, doo_img, memory_title)
        st.success("¡Guardado!")
        st.session_state.memory_image = None
    else:
        st.warning("Faltan datos.")

# --- IA & HISTORIAL ---
if st.button("✨ Generar relato IA"):
    if location and notes:
        with st.spinner("Escribiendo..."):
            try:
                st.write(generate_story(location, notes))
            except: st.error("Error en IA")

st.divider()
st.header("📚 Historial")
for e in reversed(get_entries()):
    with st.expander(f"{e['date']} - {e['location']}"):
        st.write(e['text'])
        c1, c2 = st.columns(2)
        if e.get('memory_path'): 
            c1.image(e['memory_path'], caption=e.get('memory_title', 'Recuerdo'))
        if e.get('doodle_path'): 
            c2.image(e['doodle_path'], caption="Vibes")

st.header("🌍 Recomendaciones")
dest = st.text_input("¿Próximo destino?")
if st.button("Buscar") and dest:
    try: st.write(get_recommendations(dest))
    except: st.error("Error buscando")
