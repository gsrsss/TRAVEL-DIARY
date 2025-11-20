import streamlit as st
from diary_logic import save_entry, get_entries
from travel_api import generate_story, get_recommendations

st.title("📘 Travel Diary – Diario de Viajes IA")
st.write("Guarda tus experiencias, fotos y recuerdos. La IA te ayuda a escribirlas.")

st.header("✍️ ¿Que nuevo lugar visitaste?")

date = st.date_input("Fecha del viaje")
location = st.text_input("Lugar visitado")
notes = st.text_area("Escribe tus notas o experiencias")

if st.button("Guardar entrada"):
    save_entry(str(date), location, notes)
    st.success("Entrada guardada!")

if st.button("Generar relato con IA"):
    if location and notes:
        story = generate_story(location, notes)
        st.write("### 📝 Relato generado")
        st.write(story)
    else:
        st.error("Debes ingresar lugar y notas.")

st.header("📚 Tu diario")

entries = get_entries()
for e in entries:
    st.subheader(f"{e['date']} — {e['location']}")
    st.write(e["text"])
    st.write("---")

st.header("🌍 Recomendaciones del lugar")
place = st.text_input("Escribe un lugar para obtener recomendaciones")
if st.button("Ver recomendaciones"):
    if place:
        recs = get_recommendations(place)
        st.write(recs)
