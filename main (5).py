import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página - debe ser la primera línea tras importar streamlit
st.set_page_config(
    page_title="Dashboard Capacitación",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def cargar_datos():
    df = pd.read_excel('Entrenamiento_R3.xlsx')
    df['Fecha de Capa'] = pd.to_datetime(df['Fecha de Capa'], errors='coerce')
    # Calcular puntaje promedio considerando columnas de expertise
    expertise_cols = [
        'Nivel de Expertise en Presentación',
        'Nivel de Expertise en Sondeo',
        'Nivel de Expertise en Argumentación',
        'Nivel de Expertise en Rebate',
        'Nivel de Expertise en Cierre'
    ]
    df['Puntaje Promedio'] = df[expertise_cols].mean(axis=1)
    return df

df = cargar_datos()

# Estilos de color personalizados (paleta suave, contraste accesible)
COLOR_BG = "#f5f7fa"
COLOR_ACCENT = "#005f73"
COLOR_BAR = "#0a9396"
COLOR_LINE = "#94d2bd"
COLOR_TEXT = "#001219"

st.markdown(
    f"""
    <style>
    .css-18e3th9 {{padding-top: 1rem; padding-bottom: 1rem; padding-left: 3rem; padding-right: 3rem;}}
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {COLOR_TEXT};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stButton > button {{
        background-color: {COLOR_ACCENT};
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True
)

st.title("📊 Dashboard de Capacitación por Asesor Evaluado")

# Sidebar para filtros
with st.sidebar:
    st.header("Filtros")
    asesores = df['Asesor Evaluado'].dropna().unique()
    asesor_seleccionado = st.selectbox("Selecciona el Asesor Evaluado:", sorted(asesores))

    # Rango de fechas con un rango dinámico
    fecha_min = df['Fecha de Capa'].min()
    fecha_max = df['Fecha de Capa'].max()
    fecha_inicio, fecha_fin = st.date_input(
        "Rango de fechas (Fecha de Capacitación):",
        value=[fecha_min, fecha_max],
        min_value=fecha_min,
        max_value=fecha_max
    )

# Filtrado de datos
df_filtrado = df[
    (df['Asesor Evaluado'] == asesor_seleccionado) &
    (df['Fecha de Capa'] >= pd.to_datetime(fecha_inicio)) &
    (df['Fecha de Capa'] <= pd.to_datetime(fecha_fin))
].sort_values('Fecha de Capa')

if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# Estadísticas clave
total_sesiones = len(df_filtrado)
duracion_total = df_filtrado['Duración de Capa'].sum()
duracion_media = df_filtrado['Duración de Capa'].mean()
puntaje_medio = df_filtrado['Puntaje Promedio'].mean()

# Mostrar métricas en columnas ordenadas
col1, col2, col3, col4 = st.columns([1,1,1,1])
col1.metric("Sesiones Totales", total_sesiones)
col2.metric("Duración Total (min)", f"{duracion_total:.1f}")
col3.metric("Duración Media (min)", f"{duracion_media:.1f}")
col4.metric("Puntaje Promedio", f"{puntaje_medio:.2f}")

st.markdown("---")

# Gráfico: Duración de sesiones (barra)
fig_duracion = px.bar(
    df_filtrado,
    x='Fecha de Capa',
    y='Duración de Capa',
    labels={'Duración de Capa': 'Duración (minutos)', 'Fecha de Capa': 'Fecha'},
    title="⏱️ Duración de Capacitación por Fecha",
    text=df_filtrado['Duración de Capa'].round(1),
    color_discrete_sequence=[COLOR_BAR]
)
fig_duracion.update_traces(textposition='outside')
fig_duracion.update_layout(
    yaxis=dict(range=[0, max(df_filtrado['Duración de Capa']) * 1.3]),
    plot_bgcolor=COLOR_BG,
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    margin=dict(t=50, b=50, l=25, r=25)
)
st.plotly_chart(fig_duracion, use_container_width=True)

# Gráfico: Puntaje promedio por sesión (línea)
fig_puntaje = px.line(
    df_filtrado,
    x='Fecha de Capa',
    y='Puntaje Promedio',
    markers=True,
    labels={'Puntaje Promedio': 'Puntaje Promedio', 'Fecha de Capa': 'Fecha'},
    title="⭐ Puntaje Promedio por Sesión",
    color_discrete_sequence=[COLOR_LINE]
)
fig_puntaje.update_layout(
    yaxis=dict(range=[0, 5]),
    plot_bgcolor=COLOR_BG,
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    margin=dict(t=50, b=50, l=25, r=25)
)
st.plotly_chart(fig_puntaje, use_container_width=True)

# Tabla con datos esenciales
st.subheader("📋 Detalles de Sesiones")
columnas_mostrar = [
    'ID', 'Evaluador', 'Fecha de Capa', 'Duración de Capa',
    'Puntaje Promedio', 'Detalles o Comentarios Adicionales'
]
st.dataframe(df_filtrado[columnas_mostrar].reset_index(drop=True), height=350)

# Comentarios detallados con buen formato
st.subheader("📝 Comentarios por Sesión")
for _, row in df_filtrado.iterrows():
    comentario = row['Detalles o Comentarios Adicionales']
    if pd.isna(comentario) or comentario.strip() == "":
        comentario = "_No hay comentarios disponibles._"
    st.markdown(f"**Sesión ID {row['ID']} ({row['Fecha de Capa'].date()}):** {comentario}")

st.markdown("---")
st.markdown(
    "<p style='font-size:0.8rem; color:#555;'>"
    "Dashboard desarrollado para ofrecer información clara, precisa y visualmente agradable. "
    "Puedes modificar los filtros para explorar diferentes datos."
    "</p>",
    unsafe_allow_html=True
)