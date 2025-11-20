import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import io 
import os

from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Travel Diary", layout="wide", page_icon="🎀")

# --- ESTILOS CSS PERSONALIZADOS (THEME CUTE) ---
st.markdown("""
<style>
    /* Importar Fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;700&display=swap');

    /* Fondo General (Color Papel Crema con Líneas de Cuaderno) */
    .stApp {
        background-color: #FFF9F0; /* Fondo base crema */
        background-image: 
            linear-gradient(to bottom, #FFE0EC 1px, transparent 1px); /* Líneas horizontales rosa */
        background-size: 100% 25px; /* Altura de cada línea (ej. 25px) */
        font-family: 'Quicksand', sans-serif;
    }

    /* Títulos Principales (Cursiva) */
    h1, h2, h3 {
        font-family: 'Pacifico', cursive !important;
        color: #FF8FAB !important; /* Rosa Pastel Intenso */
        text-shadow: 2px 2px 0px #FFFFFF;
    }

    /* Textos normales */
    p, div, label, input, textarea {
        font-family: 'Quicksand', sans-serif !important;
        color: #5D5D5D !important; /* Gris suave para lectura */
    }

    /* Botones (Estilo Burbuja/Candy) */
    .stButton>button {
        background-color: #FFC2D1 !important;
        color: white !important;
        border-radius: 20px !important;
        border: 2px solid #FF8FAB !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF8FAB !important;
        transform: scale(1.05);
    }

    /* Inputs de texto (Bordes redondeados) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
        background-color: #FFFFFF;
        border-radius: 15px;
        border: 2px solid #E0E0E0;
        color: #555;
    }

    /* Expander (Cajas de detalles) */
    .streamlit-expanderHeader {
        background-color: #FFF0F5;
        border-radius: 10px;
        color: #FF8FAB;
        font-weight: bold;
    }
    
    /* Efecto Washi Tape (Separador) */
    .washi-tape {
        height: 15px;
        background-image: repeating-linear-gradient(-45deg, #FFC2D1, #FFC2D1 10px, #FFFFFF 10px, #FFFFFF 20px);
        border-radius: 5px;
        margin: 20px 0;
        opacity: 0.7;
    }
    
    /* Tarjetas del Historial */
    .history-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
        border: 1px dashed #FFC2D1;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA DECORATIVA ---
st.markdown("<h1 style='text-align: center;'>✈️ Travel Diary ✈️", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em;'>☁️ Guarda tus recuerdos más dulces en este diario digital ☁️</p>", unsafe_allow_html=True)
st.markdown("<div class='washi-tape'></div>", unsafe_allow_html=True) 

# --- LÓGICA DE LA APP ---

def get_font(size):
    """Intenta cargar una fuente del sistema."""
    font_names = ["arial.ttf", "Verdana.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "msyh.ttc"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

# --- SECCIÓN 1: CREAR ENTRADA & IA ---
st.markdown("### 🌸 1. Nuevo Recuerdo")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 Fecha del viaje")
    with col2:
        location = st.text_input("📍 Lugar visitado")

    notes = st.text_area("💌 Querido diario... (Escribe tus notas aquí)")
    
    if st.button("✨ Embellecer mis notas con Magia IA"):
        if location and notes:
            with st.spinner("La IA está leyendo tu diario... 🐇"):
                try:
                    story_result = generate_story(location, notes)
                    st.success("¡Aquí tienes una versión literaria de tu día!")
                    st.markdown(f"""
                    <div style='background-color: white; padding: 20px; border-radius: 15px; border: 2px dashed #FFC2D1; font-style: italic; color: #555;'>
                    {story_result}
                    </div>
                    """, unsafe_allow_html=True)
                except: st.error("Oops! La IA está durmiendo...")
        else:
            st.warning("Escribe algo en las notas primero para que la IA pueda trabajar 💕")

st.markdown("<br>", unsafe_allow_html=True)

# --- SECCIÓN 2: FOTO DE RECUERDO + STAMPS ---
st.markdown("### 📸 2. Foto & Deco")

uploaded_memory_photo = st.file_uploader("Sube tu foto favorita:", type=["png", "jpg", "jpeg"], key="memory_photo_uploader")
memory_title = st.text_input("🏷️ Título de la foto:", placeholder="Ej. Comiendo Dango en Tokio 🍡")

if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

if uploaded_memory_photo:
    uploaded_memory_photo.seek(0)
    if st.session_state.memory_image is None: 
         st.session_state.memory_image = Image.open(uploaded_memory_photo)

if st.session_state.memory_image:
    
    col_img, col_tools = st.columns([1, 1])
    
    with col_img:
        st.image(st.session_state.memory_image, caption=memory_title if memory_title else "Tu Recuerdo", use_column_width=True)

    with col_tools:
        st.info("¡Hora de poner stickers y hacerla aún más tú! 💖") # Texto de info cute
        with st.expander("✨ Abrir Caja de Stickers", expanded=True):
            
            mode = st.radio("Modo:", ["Símbolos", "Texto"], horizontal=True)
            
            c_stamp1, c_stamp2 = st.columns(2)
            text_to_stamp = ""
            
            with c_stamp1:
                if mode == "Símbolos":
                    emoji_list = ["★", "♥", "☺", "✈", "♫", "❄", "☀", "✿", "⚡", "⚓", "🎀", "🍡", "🐱"]
                    text_to_stamp = st.selectbox("Elige:", emoji_list)
                else:
                    text_to_stamp = st.text_input("Texto:", "Tokio")
                
                stamp_color = st.color_picker("Color:", "#FF69B4") 
                
            with c_stamp2:
                stamp_size = st.slider("Tamaño:", 20, 200, 100)
                
            st.write("📍 Posición:")
            x_pos_pct = st.slider("↔️ Horizontal", 0, 100, 50)
            y_pos_pct = st.slider("↕️ Vertical", 0, 100, 50)

            if st.button("✅ Pegar Sticker"):
                img_copy = st.session_state.memory_image.copy().convert("RGBA")
                draw = ImageDraw.Draw(img_copy)
                font = get_font(stamp_size)
                
                img_w, img_h = img_copy.size
                x_px = int((x_pos_pct / 100) * img_w)
                y_px = int((y_pos_pct / 100) * img_h)
                
                try:
                    w_text, h_text = draw.textsize(text_to_stamp, font=font)
                except:
                    left, top, right, bottom = draw.textbbox((0, 0), text_to_stamp, font=font)
                    w_text, h_text = right - left, bottom - top
                
                final_x = x_px - (w_text / 2)
                final_y = y_px - (h_text / 2)

                draw.text((final_x, final_y), text_to_stamp, font=font, fill=stamp_color)

                st.session_state.memory_image = img_copy
                st.success("¡Qué lindo!")
                st.experimental_rerun() 

        if st.button("🗑️ Limpiar foto"):
            st.session_state.memory_image = None
            st.experimental_rerun()

else:
    st.info("¡Sube una foto para empezar a decorarla! 📸") # Texto de info cute

st.markdown("<div class='washi-tape'></div>", unsafe_allow_html=True)

# --- SECCIÓN 3: DOODLE SPACE (CENTRADO) ---
st.markdown("### 🎨 3. Doodle Space")
st.caption("Dibuja las vibras de tu viaje (Abstracto, Colores, Formas...) ✨") # Caption más cute

# 1. Controles
cd1, cd2, cd3 = st.columns(3)
doodle_bg = cd1.color_picker("Fondo", "#FFF0F5") 
brush_col = cd2.color_picker("Pincel", "#81D4FA") 
brush_sz = cd3.slider("Grosor", 1, 10, 3)

st.write(" ") # Espacio extra

# 2. CANVAS CENTRADO USANDO COLUMNAS
c_pad1, c_canvas, c_pad2 = st.columns([1, 3, 1])

with c_canvas:
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

st.markdown("<br>", unsafe_allow_html=True)

# --- GUARDAR ---
col_save_pad, col_save_btn, col_save_pad2 = st.columns([2, 2, 2])

with col_save_btn:
    if st.button("💾 Guardar en mi Diario", type="primary", use_container_width=True):
        if location and notes:
            mem_img = st.session_state.memory_image
            
            doo_img = None
            if doodle_res.image_data is not None:
                raw_doodle = Image.fromarray(doodle_res.image_data.astype("uint8"), "RGBA")
                bg = Image.new("RGBA", raw_doodle.size, tuple(int(doodle_bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,))
                doo_img = Image.alpha_composite(bg, raw_doodle)
                buf = io.BytesIO()
                doo_img.save(buf, format="PNG")
                buf.seek(0)
                doo_img = Image.open(buf)

            save_entry(str(date), location, notes, mem_img, doo_img, memory_title)
            st.balloons() 
            st.success("¡Guardado con éxito! ✨ Hora de crear nuevos recuerdos. 💕") # Mensaje de éxito cute
            st.session_state.memory_image = None
        else:
            st.warning("⚠️ Faltan datos importantes (como el Lugar o tus Notas). ¡No olvides rellenarlos! 🥺") # Warning cute

# --- EXTRAS & RECOMENDACIONES ---
st.markdown("<div class='washi-tape'></div>", unsafe_allow_html=True)
st.markdown("### 🌍 Próxima Aventura")

col_rec1, col_rec2 = st.columns([3, 1])
with col_rec1:
    dest = st.text_input("¿A dónde soñamos ir?", placeholder="Ej: París, Bali, Cusco...", label_visibility="collapsed")
with col_rec2:
    if st.button("🔍 Buscar ideas"):
        if dest:
            try: st.info(f"¡Qué buena idea! Aquí tienes algunas ideas para tu viaje a {dest}...") # Info cute
            except: st.error("Oopsie! No pude encontrar recomendaciones ahora mismo. ¿Pruebas otra vez? 😅") # Error cute

# --- HISTORIAL ---
st.markdown("<br><h2 style='text-align: center;'>📚 Mi Colección de Recuerdos</h2>", unsafe_allow_html=True)

for e in reversed(get_entries()):
    with st.container():
        st.markdown(f"""
        <div class="history-card">
            <h3 style="margin:0;">{e['location']}</h3>
            <p style="font-size: 0.9em; color: #888;">📅 {e['date']}</p>
            <p style="font-style: italic;">"{e['text']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if e.get('memory_path'): 
            c1.image(e['memory_path'], caption=e.get('memory_title', 'Recuerdo'), use_column_width=True)
        if e.get('doodle_path'): 
            c2.image(e['doodle_path'], caption="Mis Vibras 🎨", use_column_width=True)
        
        st.markdown("---")
