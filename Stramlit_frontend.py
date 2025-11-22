import streamlit as st
import requests
import pandas as pd

# ==========================================
# CONFIGURACIÓN
# ==========================================
API_URL = "http://127.0.0.1:8000/recommend"

# Inicializar session_state
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'recursion_level' not in st.session_state:
    st.session_state.recursion_level = 0

# ==========================================
# ESTILOS CSS
# ==========================================
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1DB954;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .song-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #1DB954;
    }
    .found-song {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1DB954;
    }
    .rec-title {
        color: #1DB954;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
    }
    .nested-rec {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border: 2px solid #ff9800;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def get_recommendations(song_name, artist_name=""):
    """Función para obtener recomendaciones de la API"""
    try:
        response = requests.post(
            API_URL,
            json={
                "song_name": song_name,
                "artist_name": artist_name
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, f"❌ {response.json()['detail']}"
        elif response.status_code == 503:
            return None, "⚠️ El servicio no está disponible. Verifica que la API esté corriendo."
        else:
            return None, f"❌ Error inesperado: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return None, "🔌 No se pudo conectar con la API. Asegúrate de que esté corriendo en http://127.0.0.1:8000"
    except requests.exceptions.Timeout:
        return None, "⏱️ La petición tardó demasiado. Intenta de nuevo."
    except Exception as e:
        return None, f"❌ Error inesperado: {str(e)}"

def display_recommendations_table(data, key_suffix=""):
    """Función para mostrar solo la tabla de recomendaciones"""
    recommendations = data['recommendations']
    
    # Crear DataFrame para la tabla interactiva
    df_display = pd.DataFrame(recommendations)
    df_display = df_display[['name', 'artists', 'year', 'popularity', 'similarity_distance']]
    df_display['year'] = df_display['year'].astype(int)
    df_display['popularity'] = df_display['popularity'].astype(int)
    df_display['similarity_distance'] = df_display['similarity_distance'].round(4)
    df_display.columns = ['Canción', 'Artista', 'Año', 'Popularidad', 'Distancia']
    
    # Mostrar tarjetas individuales
    for i, rec in enumerate(recommendations, 1):
        with st.container():
            st.markdown(f'<div class="song-card">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{i}. {rec['name']}**")
                st.markdown(f"👤 {rec['artists']}")
            
            with col2:
                st.markdown(f"📅 {int(rec['year'])}")
                st.markdown(f"⭐ Popularidad: {int(rec['popularity'])}")
            
            with col3:
                similarity = 100 - (rec['similarity_distance'] * 10)
                similarity = max(0, min(100, similarity))
                st.metric("Similitud", f"{similarity:.0f}%")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabla interactiva con selección
    st.markdown("---")
    st.markdown("### 📊 Haz clic en una canción para ver sus recomendaciones")
    
    # Usar dataframe con selección de eventos
    event = st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=False,
        on_select="rerun",
        selection_mode="single-row",
        key=f"dataframe_{key_suffix}"
    )
    
    # Retornar la selección
    if event.selection and len(event.selection.rows) > 0:
        selected_idx = event.selection.rows[0]
        return recommendations[selected_idx]
    
    return None

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.markdown('<h1 class="main-title">🎵 Recomendador Musical</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Descubre música similar a tus canciones favoritas</p>', unsafe_allow_html=True)

# Formulario de búsqueda
with st.form("search_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        song_name = st.text_input(
            "🎸 Nombre de la canción",
            placeholder="Ej: Bohemian Rhapsody",
            help="Introduce el nombre de la canción"
        )
    
    with col2:
        artist_name = st.text_input(
            "👤 Artista (opcional)",
            placeholder="Ej: Queen",
            help="Ayuda a encontrar la canción exacta"
        )
    
    submitted = st.form_submit_button("🔍 Buscar Recomendaciones", use_container_width=True)

# ==========================================
# LÓGICA DE BÚSQUEDA PRINCIPAL
# ==========================================
if submitted:
    if not song_name:
        st.error("⚠️ Por favor, introduce el nombre de una canción")
    else:
        st.session_state.recursion_level = 0
        with st.spinner("🎵 Buscando recomendaciones..."):
            data, error = get_recommendations(song_name, artist_name)
            
            if data:
                st.session_state.current_data = data
            elif error:
                st.error(error)
                if "No se encontró" in error:
                    st.info("💡 Intenta con otro nombre o sin especificar el artista")
                elif "No se pudo conectar" in error:
                    st.info("💡 Ejecuta la API con: `python tu_api.py`")

# ==========================================
# MOSTRAR RESULTADOS
# ==========================================
if st.session_state.current_data:
    data = st.session_state.current_data
    
    # Mostrar canción encontrada
    st.markdown('<div class="found-song">', unsafe_allow_html=True)
    st.markdown("### ✅ Canción encontrada")
    found = data['song_found']
    st.markdown(f"**🎵 {found['name']}**")
    st.markdown(f"👤 {found['artist']}")
    st.markdown(f"📅 Año: {found['year']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar recomendaciones
    st.markdown('<h2 class="rec-title">🎯 Recomendaciones para ti:</h2>', unsafe_allow_html=True)
    
    # Mostrar tabla y obtener selección
    selected_song = display_recommendations_table(data, key_suffix="main")
    
    # Si se seleccionó una canción, buscar automáticamente
    if selected_song:
        st.markdown('<div class="nested-rec">', unsafe_allow_html=True)
        st.markdown(f"### 🔄 Recomendaciones basadas en: **{selected_song['name']}**")
        st.markdown(f"**Artista:** {selected_song['artists']}")
        
        with st.spinner("🎵 Cargando recomendaciones..."):
            nested_data, nested_error = get_recommendations(selected_song['name'], selected_song['artists'])
            
            if nested_data:
                # Mostrar canción encontrada para la selección
                st.markdown("---")
                nested_found = nested_data['song_found']
                st.markdown(f"✅ **{nested_found['name']}** - {nested_found['artist']} ({nested_found['year']})")
                
                # Mostrar recomendaciones anidadas
                selected_nested = display_recommendations_table(nested_data, key_suffix="nested")
                
                # Tercer nivel de recomendaciones
                if selected_nested:
                    st.markdown("---")
                    st.markdown(f"### 🔄🔄 Explorando: **{selected_nested['name']}**")
                    
                    with st.spinner("🎵 Cargando más recomendaciones..."):
                        third_data, third_error = get_recommendations(selected_nested['name'], selected_nested['artists'])
                        
                        if third_data:
                            third_found = third_data['song_found']
                            st.markdown(f"✅ **{third_found['name']}** - {third_found['artist']}")
                            display_recommendations_table(third_data, key_suffix="third")
                        elif third_error:
                            st.error(third_error)
            
            elif nested_error:
                st.error(nested_error)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# INFORMACIÓN ADICIONAL
# ==========================================
with st.sidebar:
    st.markdown("### ℹ️ Información")
    st.markdown("""
    Esta aplicación utiliza Machine Learning (KNN) 
    para recomendar canciones similares basándose en 
    características musicales como:
    
    - 🎼 Tempo
    - 🎹 Tonalidad
    - 🔊 Energía
    - 💃 Bailabilidad
    - 🎤 Acústica
    - Y más...
    """)
    
    st.markdown("---")
    st.markdown("### 🚀 Cómo usar")
    st.markdown("""
    1. Escribe el nombre de una canción
    2. (Opcional) Añade el artista
    3. Haz clic en buscar
    4. **¡Haz clic en cualquier fila de la tabla!**
    5. Se cargarán automáticamente las recomendaciones
    6. ¡Puedes explorar hasta 3 niveles!
    """)
    
    st.markdown("---")
    st.markdown("### 🔧 Estado del sistema")
    try:
        health = requests.get("http://127.0.0.1:8000/", timeout=2)
        if health.status_code == 200:
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ API responde con errores")
    except:
        st.error("❌ API desconectada")