import streamlit as st
import pandas as pd
import plotly.express as px  # Import necesario para gráficos

st.set_page_config(page_title="Dashboard Capacitación", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_excel('Entrenamiento_R3.xlsx')
    df['Fecha de Capa'] = pd.to_datetime(df['Fecha de Capa'], errors='coerce')
    return df

def mostrar_valor(valor):
    if pd.isna(valor):
        return "No disponible"
    if isinstance(valor, str) and valor.strip() == '':
        return "No disponible"
    return valor

df = cargar_datos()

st.title("📋 Informe de Capacitación por Asesor Evaluado")

asesores = df['Asesor Evaluado'].dropna().unique()
asesor_seleccionado = st.selectbox("🔍 Selecciona el Asesor Evaluado:", sorted(asesores))

df_asesor = df[df['Asesor Evaluado'] == asesor_seleccionado].sort_values('Fecha de Capa')

if df_asesor.empty:
    st.warning("⚠️ No hay datos para el asesor seleccionado.")
else:
    # Resumen general
    total_sesiones = len(df_asesor)
    duracion_total = df_asesor['Duración de Capa'].sum()
    duracion_media = df_asesor['Duración de Capa'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Sesiones Totales", total_sesiones)
    col2.metric("Duración Total (min)", f"{duracion_total:.1f}")
    col3.metric("Duración Media (min)", f"{duracion_media:.1f}")

    st.markdown("---")

    # Gráfico 1: Sesiones por fecha
    sesiones_por_fecha = df_asesor.groupby('Fecha de Capa').size().reset_index(name='Cantidad de Sesiones')
    fig_sesiones = px.bar(
        sesiones_por_fecha,
        x='Fecha de Capa',
        y='Cantidad de Sesiones',
        title="Número de Sesiones por Fecha",
        labels={'Cantidad de Sesiones': 'Cantidad', 'Fecha de Capa': 'Fecha'}
    )
    st.plotly_chart(fig_sesiones, use_container_width=True)

    # Gráfico 2: Duración total por fecha
    duracion_por_fecha = df_asesor.groupby('Fecha de Capa')['Duración de Capa'].sum().reset_index()
    fig_duracion = px.bar(
        duracion_por_fecha,
        x='Fecha de Capa',
        y='Duración de Capa',
        title="Duración Total de Sesiones por Fecha (minutos)",
        labels={'Duración de Capa': 'Duración (min)', 'Fecha de Capa': 'Fecha'}
    )
    st.plotly_chart(fig_duracion, use_container_width=True)

    # Gráfico 3: Conteo respuestas Mandamientos
    mandamientos = df_asesor['¿Cumple los 6 Mandamientos de la Venta Carrión?'].dropna()
    if not mandamientos.empty:
        conteo_mandamientos = mandamientos.value_counts().reset_index()
        conteo_mandamientos.columns = ['Respuesta', 'Frecuencia']
        fig_mandamientos = px.bar(
            conteo_mandamientos,
            x='Respuesta',
            y='Frecuencia',
            title="Distribución de respuestas a '¿Cumple los 6 Mandamientos de la Venta Carrión?'",
            labels={'Frecuencia': 'Cantidad', 'Respuesta': 'Respuesta'}
        )
        st.plotly_chart(fig_mandamientos, use_container_width=True)
    else:
        st.info("No hay datos para '¿Cumple los 6 Mandamientos de la Venta Carrión?'.")

    st.markdown("---")

    # Mostrar detalle textual por sesión sin gráficos de criterios
    for idx, row in df_asesor.iterrows():
        fecha_str = row['Fecha de Capa'].strftime('%d-%m-%Y') if pd.notna(row['Fecha de Capa']) else "Fecha desconocida"
        with st.expander(f"Sesión del {fecha_str} - Evaluador: {mostrar_valor(row.get('Evaluador'))} - Duración: {mostrar_valor(row.get('Duración de Capa'))} min"):
            st.markdown(f"**Presentación:** {mostrar_valor(row.get('Nivel de Expertise en Presentación'))}")
            st.markdown(f"**Sondeo:** {mostrar_valor(row.get('Nivel de Expertise en Sondeo'))}")
            st.markdown(f"**Argumentación:** {mostrar_valor(row.get('Nivel de Expertise en Argumentación'))}")
            st.markdown(f"**Rebate:** {mostrar_valor(row.get('Nivel de Expertise en Rebate'))}")
            st.markdown(f"**Cierre:** {mostrar_valor(row.get('Nivel de Expertise en Cierre'))}")
            st.markdown(f"**¿Cumple los 6 Mandamientos de la Venta Carrión?:** {mostrar_valor(row.get('¿Cumple los 6 Mandamientos de la Venta Carrión?'))}")
            st.markdown(f"**¿Cuál o cuáles mandamientos NO cumple?:** {mostrar_valor(row.get('¿Cuál o cuáles mandamientos NO cumple?'))}")
            comentarios = mostrar_valor(row.get('Detalles o Comentarios Adicionales'))
            st.markdown(f"**Comentarios adicionales:** {comentarios}")
            st.markdown("---")
