import streamlit as st
from PIL import Image, ImageDraw, ImageFont # Asegúrate de que ImageFont esté disponible
from streamlit_drawable_canvas import st_canvas
import io # Necesario para manejar la imagen del doodle

# Importaciones locales
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

# --- Configuración de la página ---
st.set_page_config(layout="wide") # Opcional: usar layout ancho para más espacio
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

# --- SECCIÓN DE FOTO DE RECUERDO (SOLO MOSTRAR) ---
st.subheader("📸 Sube una foto como recuerdo")
uploaded_memory_photo = st.file_uploader("Elige una imagen para tu recuerdo:", type=["png", "jpg", "jpeg"], key="memory_photo_uploader")

# Almacenamos la imagen del recuerdo en session_state para que persista
if 'memory_image' not in st.session_state:
    st.session_state.memory_image = None

if uploaded_memory_photo:
    uploaded_memory_photo.seek(0) # Resetear puntero
    st.session_state.memory_image = Image.open(uploaded_memory_photo)
    st.image(st.session_state.memory_image, caption="Foto de Recuerdo", use_column_width=True)
else:
    st.session_state.memory_image = None # Limpiar si no hay foto

# --- SECCIÓN DE DOODLE SPACE (PARA DIBUJAR LIBREMENTE) ---
st.subheader("🎨 Doodle Space: Ilustra las vibras de tu viaje")

col_doodle_controls_1, col_doodle_controls_2, col_doodle_controls_3 = st.columns(3)

with col_doodle_controls_1:
    doodle_bg_color = st.color_picker("Color de fondo del doodle:", "#F0F2F6") # Un gris claro por defecto
with col_doodle_controls_2:
    doodle_stroke_color = st.color_picker("Color del pincel:", "#000000")
with col_doodle_controls_3:
    doodle_stroke_width = st.slider("Grosor del pincel:", 1, 10, 3)

doodle_width = 700
doodle_height = 400

# Herramienta de texto
st.markdown("---")
st.markdown("### 📝 Añadir Texto al Doodle")
text_to_add = st.text_input("Escribe el texto que quieres añadir:")
text_color = st.color_picker("Color del texto:", "#FF0000")
font_size = st.slider("Tamaño del texto:", 10, 50, 20)
font_family = st.selectbox("Fuente:", ["Arial", "Courier New", "Verdana", "Times New Roman"], index=0)

# El Canvas para el Doodle
st.write("👇 ¡Dibuja aquí abajo!")
doodle_canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)", # Sin relleno para formas
    stroke_width=doodle_stroke_width,
    stroke_color=doodle_stroke_color,
    background_color=doodle_bg_color, # Usamos el color de fondo elegido
    update_streamlit=True,
    height=doodle_height,
    width=doodle_width,
    drawing_mode="freedraw", # Solo dibujo libre
    key="doodle_canvas",
)

# Inicializamos el resultado final del doodle
doodle_final_image_to_save = None

# Procesar el doodle y añadir texto si aplica
if doodle_canvas_result.image_data is not None:
    # Convertir el resultado del canvas a una imagen PIL
    doodle_image = Image.fromarray(doodle_canvas_result.image_data.astype("uint8"), "RGBA")

    # Si hay texto para añadir, creamos una imagen temporal para el texto
    if text_to_add:
        # Creamos una imagen base con el color de fondo elegido para el texto
        # Convertimos el color hexadecimal a RGB
        bg_rgb = tuple(int(doodle_bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_base_image = Image.new("RGBA", doodle_image.size, bg_rgb + (255,)) # Fondo opaco

        draw = ImageDraw.Draw(text_base_image)
        try:
            # Intentar cargar una fuente. Si no se encuentra, usa la predeterminada.
            font = ImageFont.truetype(f"{font_family.lower()}.ttf", font_size)
        except IOError:
            st.warning(f"No se pudo cargar la fuente '{font_family}'. Usando la predeterminada.")
            font = ImageFont.load_default() # Fuente predeterminada

        # Calcular posición para centrar el texto (simplificado)
        text_width, text_height = draw.textsize(text_to_add, font=font)
        x = (doodle_image.width - text_width) / 2
        y = (doodle_image.height - text_height) / 2
        
        draw.text((x, y), text_to_add, font=font, fill=text_color)
        
        # Combinar el texto con el doodle
        doodle_final_image_to_save = Image.alpha_composite(text_base_image, doodle_image)
    else:
        # Si no hay texto, el doodle_image es el final
        doodle_final_image_to_save = doodle_image

# --- BOTÓN DE GUARDAR ---
if st.button("Guardar entrada"):
    if location and notes:
        # Guardamos la foto de recuerdo si existe
        memory_image_to_save = st.session_state.memory_image

        # Guardamos el doodle final si existe y tiene contenido
        doodle_to_save = None
        if doodle_final_image_to_save:
            # Convertimos el doodle RGBA a un formato guardable (PNG)
            # Y luego a BytesIO para pasarlo a save_entry
            doodle_bytes_io = io.BytesIO()
            doodle_final_image_to_save.save(doodle_bytes_io, format="PNG")
            doodle_bytes_io.seek(0)
            doodle_to_save = Image.open(doodle_bytes_io) # Re-abrimos como PIL para save_entry
            
        save_entry(str(date), location, notes, memory_image_to_save, doodle_to_save)
        st.success("¡Entrada guardada!")
        
        # Limpiar el estado después de guardar para una nueva entrada limpia
        st.session_state.memory_image = None
        # Opcional: recargar la página para limpiar el uploader y canvas
        # st.experimental_rerun()
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
        if e.get("memory_image_path"): # Nuevo nombre para la foto de recuerdo
            try:
                st.image(e["memory_image_path"], caption="Foto de Recuerdo", use_column_width=True)
            except:
                st.write("🖼️ (Imagen de recuerdo no disponible)")
        if e.get("doodle_image_path"): # Nuevo nombre para el doodle
            try:
                st.image(e["doodle_image_path"], caption="Doodle del Viaje", use_column_width=True)
            except:
                st.write("🎨 (Doodle no disponible)")
        st.write("---")

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
