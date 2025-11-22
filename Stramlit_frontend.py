import streamlit as st
import requests
import pandas as pd

# ==========================================
# CONFIGURACIÓN
# ==========================================
API_URL = "http://127.0.0.1:8000/recommend"

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
    </style>
""", unsafe_allow_html=True)

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
# LÓGICA DE BÚSQUEDA
# ==========================================
if submitted:
    if not song_name:
        st.error("⚠️ Por favor, introduce el nombre de una canción")
    else:
        with st.spinner("🎵 Buscando recomendaciones..."):
            try:
                # Petición a la API
                response = requests.post(
                    API_URL,
                    json={
                        "song_name": song_name,
                        "artist_name": artist_name
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
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
                    
                    recommendations = data['recommendations']
                    
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
                    
                    # Tabla resumen (opcional)
                    with st.expander("📊 Ver tabla completa"):
                        df = pd.DataFrame(recommendations)
                        df = df[['name', 'artists', 'year', 'popularity', 'similarity_distance']]
                        df.columns = ['Canción', 'Artista', 'Año', 'Popularidad', 'Distancia']
                        st.dataframe(df, use_container_width=True)
                
                elif response.status_code == 404:
                    st.error(f"❌ {response.json()['detail']}")
                    st.info("💡 Intenta con otro nombre o sin especificar el artista")
                
                elif response.status_code == 503:
                    st.error("⚠️ El servicio no está disponible. Verifica que la API esté corriendo.")
                
                else:
                    st.error(f"❌ Error inesperado: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                st.error("🔌 No se pudo conectar con la API. Asegúrate de que esté corriendo en http://127.0.0.1:8000")
                st.info("💡 Ejecuta la API con: `python tu_api.py`")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ La petición tardó demasiado. Intenta de nuevo.")
            
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")

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
    4. ¡Disfruta de las recomendaciones!
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