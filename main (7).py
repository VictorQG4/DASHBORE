import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# Configuración de página
st.set_page_config(page_title="Dashboard Capacitación", layout="wide")

@st.cache_data
def cargar_datos():
    # Leer archivo Excel
    df = pd.read_excel('Entrenamiento_R3.xlsx')

    # Convertir fechas
    df['Fecha de Capa'] = pd.to_datetime(df['Fecha de Capa'], errors='coerce')

    # Crear columna de Puntaje Promedio basado en criterios individuales
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

st.title("📊 Dashboard de Capacitación por Asesor Evaluado")

# Selección de asesor evaluado
asesores = df['Asesor Evaluado'].dropna().unique()
asesor_seleccionado = st.selectbox("🔎 Selecciona el Asesor Evaluado:", sorted(asesores))

# Filtrar datos por asesor seleccionado y ordenar por fecha
df_asesor = df[df['Asesor Evaluado'] == asesor_seleccionado].sort_values('Fecha de Capa')

if df_asesor.empty:
    st.warning("⚠️ No se encontraron datos para el asesor seleccionado.")
else:
    # Estadísticas generales
    total_sesiones = len(df_asesor)
    duracion_total = df_asesor['Duración de Capa'].sum()
    duracion_media = df_asesor['Duración de Capa'].mean()
    puntaje_medio = df_asesor['Puntaje Promedio'].mean()

    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesiones Totales", total_sesiones)
    col2.metric("Duración Total (min)", f"{duracion_total:.1f}")
    col3.metric("Duración Media (min)", f"{duracion_media:.1f}")
    col4.metric("Puntaje Promedio", f"{puntaje_medio:.2f}")

    st.markdown("---")

    # Gráfico 1: Duración de sesiones a lo largo del tiempo
    fig_duracion = px.bar(
        df_asesor,
        x='Fecha de Capa',
        y='Duración de Capa',
        title="Duración de Capacitación por Fecha",
        labels={'Duración de Capa': 'Duración (minutos)', 'Fecha de Capa': 'Fecha'},
        text='Duración de Capa'
    )
    fig_duracion.update_traces(textposition='outside')
    fig_duracion.update_layout(yaxis_range=[0, max(df_asesor['Duración de Capa']) * 1.2])
    st.plotly_chart(fig_duracion, use_container_width=True)

    # Gráfico 2: Puntajes por criterio (solo los niveles numéricos)
    criterios = [
        'Nivel de Expertise en Presentación',
        'Nivel de Expertise en Sondeo',
        'Nivel de Expertise en Argumentación',
        'Nivel de Expertise en Rebate',
        'Nivel de Expertise en Cierre'
    ]

    df_melt = df_asesor.melt(
        id_vars=['Fecha de Capa'],
        value_vars=criterios,
        var_name='Criterio',
        value_name='Puntaje'
    )
    df_melt['Criterio'] = df_melt['Criterio'].str.replace('Nivel de Expertise en ', '')

    fig_criterios = px.line(
        df_melt,
        x='Fecha de Capa',
        y='Puntaje',
        color='Criterio',
        markers=True,
        title="Evolución de Puntajes por Criterio",
        labels={'Puntaje': 'Puntaje', 'Fecha de Capa': 'Fecha'}
    )
    fig_criterios.update_layout(yaxis_range=[0, 5])
    st.plotly_chart(fig_criterios, use_container_width=True)

    # Tabla con toda la información requerida
    columnas_mostrar = [
        'Fecha de Capa',
        'Duración de Capa',
        'Evaluador',
        'Nivel de Expertise en Presentación',
        'Nivel de Expertise en Sondeo',
        'Nivel de Expertise en Argumentación',
        'Nivel de Expertise en Rebate',
        'Nivel de Expertise en Cierre',
        '¿Cumple los 6 Mandamientos de la Venta Carrión?',
        '¿Cuál o cuáles mandamientos NO cumple?',
        'Detalles o Comentarios Adicionales'
    ]

    st.subheader("📋 Detalles de Sesiones")
    st.dataframe(df_asesor[columnas_mostrar].reset_index(drop=True), height=400)

    # Comentarios por sesión
    st.subheader("📝 Comentarios por Sesión")
    for idx, row in df_asesor.iterrows():
        comentario = row['Detalles o Comentarios Adicionales']
        if pd.isna(comentario) or comentario.strip() == '':
            comentario = "_No hay comentarios._"
        fecha_str = row['Fecha de Capa'].strftime('%d-%m-%Y')
        st.markdown(f"**Sesión del {fecha_str} (Evaluador: {row['Evaluador']}):** {comentario}")

    st.markdown("---")

    # Resumen Mandamientos No Cumplidos
    st.subheader("⚠️ Mandamientos No Cumplidos - Resumen")
    mandamientos = df_asesor['¿Cuál o cuáles mandamientos NO cumple?'].dropna()
    if mandamientos.empty:
        st.info("No hay registros de mandamientos no cumplidos para este asesor.")
    else:
        # Dividir por comas o punto y coma, quitar espacios
        mandamientos_list = mandamientos.str.split('[,;]').explode().str.strip()
        conteo = Counter(mandamientos_list)
        resumen_df = pd.DataFrame(conteo.items(), columns=['Mandamiento', 'Frecuencia']).sort_values(by='Frecuencia', ascending=False)
        st.table(resumen_df.reset_index(drop=True))