# --- EXTRAS ---
st.markdown("<div class='washi-tape'></div>", unsafe_allow_html=True)
st.markdown("### 🌍 Próxima Aventura")

# 1. Creamos las columnas solo para el buscador y el botón
col_rec1, col_rec2 = st.columns([3, 1])

with col_rec1:
    dest = st.text_input("¿A dónde soñamos ir?", placeholder="Ej: París, Tokio...", label_visibility="collapsed")

with col_rec2:
    # Guardamos si se hizo clic en una variable
    search_click = st.button("🔍 Buscar ideas", use_container_width=True)

# 2. La lógica de mostrar resultados está FUERA de las columnas (se verá abajo)
if search_click:
    if dest:
        with st.spinner("Consultando al oráculo viajero... 🔮"):
            try: 
                recs = get_recommendations(dest) 
                
                # Espacio visual extra
                st.markdown("<br>", unsafe_allow_html=True) 
                
                # Resultados ocupando todo el ancho
                st.info(f"¡Aquí tienes ideas para {dest}! 👇")
                st.markdown(f"""
                <div style='background-color: white; padding: 20px; border-radius: 15px; border: 2px dashed #81D4FA; color: #555;'>
                {recs}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e: 
                st.error(f"Oopsie! {e}")
