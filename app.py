import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
from diary_logic import save_entry, get_entries
# from travel_api import generate_story, get_recommendations # Descomentar si usas la API

st.set_page_config(page_title="Travel Diary", layout="centered")
st.title("📘 Travel Diary IA")

if 'mem_img' not in st.session_state: st.session_state.mem_img = None

# --- ENTRADA DE DATOS ---
c1, c2 = st.columns(2)
date = c1.date_input("Fecha")
location = c2.text_input("Lugar")
notes = st.text_area("Notas del viaje")

# --- 1. FOTO DE RECUERDO ---
st.subheader("📸 Tu Recuerdo")
uploaded = st.file_uploader("Sube una foto", type=["jpg", "png"], key="mem_up")

# --- CAMBIO AQUÍ: Input para el nombre de la foto ---
mem_title = st.text_input("Título de este recuerdo (Opcional)", placeholder="Ej. Atardecer en Kioto")

if uploaded:
    uploaded.seek(0)
    st.session_state.mem_img = Image.open(uploaded)

if st.session_state.mem_img:
    st.image(st.session_state.mem_img, caption=mem_title if mem_title else "Vista previa", use_column_width=True)

# --- 2. DOODLE SPACE ---
st.subheader("🎨 Doodle Space & Vibes")
dc1, dc2, dc3 = st.columns(3)
bg_col = dc1.color_picker("Fondo", "#F0F2F6")
brush_col = dc2.color_picker("Pincel", "#000000")
width = dc3.slider("Grosor", 1, 20, 3)

with st.expander("🔤 Añadir texto al dibujo"):
    tc1, tc2, tc3 = st.columns([3,1,1])
    txt_input = tc1.text_input("Texto")
    txt_col = tc2.color_picker("Color Txt", "#FF0000")
    txt_size = tc3.number_input("Tamaño", 10, 100, 20)

canvas = st_canvas(
    fill_color="rgba(0,0,0,0)", stroke_width=width, stroke_color=brush_col,
    background_color=bg_col, height=400, width=700, drawing_mode="freedraw",
    key="doodle_canvas"
)

# --- GUARDADO ---
if st.button("💾 Guardar Entrada", type="primary"):
    if location and notes:
        final_doodle = None
        if canvas.image_data is not None:
            img = Image.fromarray(canvas.image_data.astype("uint8"), "RGBA")
            if txt_input:
                base = Image.new("RGBA", img.size, tuple(int(bg_col.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (255,))
                draw = ImageDraw.Draw(base)
                try: font = ImageFont.truetype("arial.ttf", txt_size)
                except: font = ImageFont.load_default()
                w_t, h_t = draw.textsize(txt_input, font=font) if hasattr(draw, 'textsize') else (0,0) 
                draw.text(((img.width-w_t)/2, (img.height-h_t)/2), txt_input, font=font, fill=txt_col)
                final_doodle = Image.alpha_composite(base, img)
            else:
                final_doodle = img

        # --- CAMBIO AQUÍ: Pasamos mem_title a la función ---
        save_entry(date, location, notes, st.session_state.mem_img, final_doodle, mem_title)
        
        st.success("¡Guardado!")
        st.session_state.mem_img = None
    else:
        st.warning("Falta lugar o notas.")

# --- HISTORIAL ---
st.divider()
st.header("📚 Historial")
for e in reversed(get_entries()):
    with st.expander(f"{e['date']} - {e['location']}"):
        st.write(e['text'])
        c_img1, c_img2 = st.columns(2)
        
        # --- CAMBIO AQUÍ: Mostrar el título guardado ---
        if e.get('memory_path'): 
            title_display = e.get('memory_title') if e.get('memory_title') else "Recuerdo"
            c_img1.image(e['memory_path'], caption=title_display)
            
        if e.get('doodle_path'): 
            c_img2.image(e['doodle_path'], caption="Vibes/Doodle")
