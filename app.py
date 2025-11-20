import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations # Asumiendo que existe

st.set_page_config(page_title="Travel Diary", layout="centered")
st.title("📘 Travel Diary IA")

# --- ESTADO DE SESIÓN ---
if 'mem_img' not in st.session_state: st.session_state.mem_img = None

# --- ENTRADA DE DATOS ---
c1, c2 = st.columns(2)
date = c1.date_input("Fecha")
location = c2.text_input("Lugar")
notes = st.text_area("Notas del viaje")

# --- 1. FOTO DE RECUERDO ---
uploaded = st.file_uploader("📸 Foto del recuerdo", type=["jpg", "png"], key="mem_up")
if uploaded:
    uploaded.seek(0)
    st.session_state.mem_img = Image.open(uploaded)

if st.session_state.mem_img:
    st.image(st.session_state.mem_img, caption="Tu Recuerdo", use_column_width=True)

# --- 2. DOODLE SPACE ---
st.subheader("🎨 Doodle Space & Vibes")
dc1, dc2, dc3 = st.columns(3)
bg_col = dc1.color_picker("Fondo", "#F0F2F6")
brush_col = dc2.color_picker("Pincel", "#000000")
width = dc3.slider("Grosor", 1, 20, 3)

# Herramientas de Texto
with st.expander("🔤 Añadir texto al dibujo"):
    tc1, tc2, tc3 = st.columns([3,1,1])
    txt_input = tc1.text_input("Texto")
    txt_col = tc2.color_picker("Color Txt", "#FF0000")
    txt_size = tc3.number_input("Tamaño", 10, 100, 20)

# Canvas
canvas = st_canvas(
    fill_color="rgba(0,0,0,0)", stroke_width=width, stroke_color=brush_col,
    background_color=bg_col, height=400, width=700, drawing_mode="freedraw",
    key="doodle_canvas"
)

# --- GUARDADO ---
if st.button("💾 Guardar Entrada", type="primary"):
    if location and notes:
        final_doodle = None
        # Procesar Doodle + Texto
        if canvas.image_data is not None:
            img = Image.fromarray(canvas.image_data.astype("uint8"), "RGBA")
            # Si hay texto, lo escribimos sobre el doodle
            if txt_input:
                # Crear fondo sólido para combinar correctamente alphas
                base = Image.new("RGBA", img.size, tuple(int(bg_col.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (255,))
                draw = ImageDraw.Draw(base)
                try: font = ImageFont.truetype("arial.ttf", txt_size)
                except: font = ImageFont.load_default()
                # Centrar texto simple
                w_t, h_t = draw.textsize(txt_input, font=font) if hasattr(draw, 'textsize') else (0,0) 
                draw.text(((img.width-w_t)/2, (img.height-h_t)/2), txt_input, font=font, fill=txt_col)
                final_doodle = Image.alpha_composite(base, img)
            else:
                final_doodle = img

        save_entry(date, location, notes, st.session_state.mem_img, final_doodle)
        st.success("¡Guardado!")
        st.session_state.mem_img = None # Reset
    else:
        st.warning("Falta lugar o notas.")

# --- IA & VISUALIZACIÓN ---
if st.button("✨ Generar Historia IA"):
    if location and notes: st.write(generate_story(location, notes))

st.divider()
st.header("📚 Historial")
for e in reversed(get_entries()):
    with st.expander(f"{e['date']} - {e['location']}"):
        st.write(e['text'])
        c_img1, c_img2 = st.columns(2)
        if e.get('memory_path'): c_img1.image(e['memory_path'], caption="Recuerdo")
        if e.get('doodle_path'): c_img2.image(e['doodle_path'], caption="Vibes/Doodle")

st.divider()
dest = st.text_input("¿Próximo destino?")
if st.button("🔍 Recomendaciones") and dest:
    st.write(get_recommendations(dest))
