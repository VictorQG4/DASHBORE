import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Capacitación", layout="wide")

st.title("📋 Informe de Capacitación por Asesor Evaluado")

def mostrar_valor(valor):
    if pd.isna(valor):
        return "No disponible"
    if isinstance(valor, str) and valor.strip() == '':
        return "No disponible"
    return valor

# Ruta relativa al archivo (debe estar en la misma carpeta que este script)
archivo_excel = "Entrenamiento_R3.xlsx"

if not os.path.exists(archivo_excel):
    st.error(f"Archivo '{archivo_excel}' no encontrado en la carpeta actual.")
    st.stop()

df = pd.read_excel(archivo_excel)
df['Fecha de Capa'] = pd.to_datetime(df['Fecha de Capa'], errors='coerce')

asesores = df['Asesor Evaluado'].dropna().unique()
asesor_seleccionado = st.selectbox("🔍 Selecciona el Asesor Evaluado:", sorted(asesores))

df_asesor = df[df['Asesor Evaluado'] == asesor_seleccionado].sort_values('Fecha de Capa')

if df_asesor.empty:
    st.warning("⚠️ No hay datos para el asesor seleccionado.")
else:
    total_sesiones = len(df_asesor)
    duracion_total = df_asesor['Duración de Capa'].sum()
    duracion_media = df_asesor['Duración de Capa'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Sesiones Totales", total_sesiones)
    col2.metric("Duración Total (minutos)", f"{duracion_total:.1f}")
    col3.metric("Duración Media (minutos)", f"{duracion_media:.1f}")

    st.markdown("---")

    sesiones_por_fecha = df_asesor.groupby('Fecha de Capa').size().reset_index(name='Cantidad de Sesiones')
    fig_sesiones = px.bar(
        sesiones_por_fecha,
        x='Fecha de Capa',
        y='Cantidad de Sesiones',
        title="Número de Sesiones por Fecha",
        labels={'Cantidad de Sesiones': 'Cantidad', 'Fecha de Capa': 'Fecha'},
        template='plotly_white'
    )
    st.plotly_chart(fig_sesiones, use_container_width=True)

    duracion_por_fecha = df_asesor.groupby('Fecha de Capa')['Duración de Capa'].sum().reset_index()
    fig_duracion = px.bar(
        duracion_por_fecha,
        x='Fecha de Capa',
        y='Duración de Capa',
        title="Duración Total de Sesiones por Fecha (minutos)",
        labels={'Duración de Capa': 'Duración (min)', 'Fecha de Capa': 'Fecha'},
        template='plotly_white'
    )
    st.plotly_chart(fig_duracion, use_container_width=True)

    st.subheader("Evaluadores y detalles de las sesiones")
    evaluadores_tabla = df_asesor[['Fecha de Capa', 'Evaluador', 'Duración de Capa']].copy()
    evaluadores_tabla['Fecha de Capa'] = evaluadores_tabla['Fecha de Capa'].dt.strftime('%d-%m-%Y')
    evaluadores_tabla.rename(columns={
        'Fecha de Capa': 'Fecha de Capacitación',
        'Evaluador': 'Evaluador',
        'Duración de Capa': 'Duración (minutos)'
    }, inplace=True)
    st.dataframe(evaluadores_tabla.reset_index(drop=True), height=200)

    st.markdown("---")

    st.subheader("Detalle por sesión y criterios evaluados")
    for idx, row in df_asesor.iterrows():
        fecha_str = row['Fecha de Capa'].strftime('%d-%m-%Y') if pd.notna(row['Fecha de Capa']) else "Fecha desconocida"
        with st.expander(f"Sesión del {fecha_str} - Evaluador: {mostrar_valor(row.get('Evaluador'))} - Duración: {mostrar_valor(row.get('Duración de Capa'))} min"):
            st.markdown(f"**Presentación:** {mostrar_valor(row.get('Presentación'))}")
            st.markdown(f"**Nivel de Expertise en Presentación:** {mostrar_valor(row.get('Nivel de Expertise en Presentación'))}")

            st.markdown(f"**Sondeo:** {mostrar_valor(row.get('Sondeo'))}")
            st.markdown(f"**Nivel de Expertise en Sondeo:** {mostrar_valor(row.get('Nivel de Expertise en Sondeo'))}")

            st.markdown(f"**Argumentación:** {mostrar_valor(row.get('Argumentación'))}")
            st.markdown(f"**Nivel de Expertise en Argumentación:** {mostrar_valor(row.get('Nivel de Expertise en Argumentación'))}")

            st.markdown(f"**Rebate:** {mostrar_valor(row.get('Rebate'))}")
            st.markdown(f"**Nivel de Expertise en Rebate:** {mostrar_valor(row.get('Nivel de Expertise en Rebate'))}")

            st.markdown(f"**Cierre:** {mostrar_valor(row.get('Cierre'))}")
            st.markdown(f"**Nivel de Expertise en Cierre:** {mostrar_valor(row.get('Nivel de Expertise en Cierre'))}")

            st.markdown(f"**¿Cumple los 6 Mandamientos de la Venta Carrión?:** {mostrar_valor(row.get('¿Cumple los 6 Mandamientos de la Venta Carrión?'))}")
            st.markdown(f"**¿Cuál o cuáles mandamientos NO cumple?:** {mostrar_valor(row.get('¿Cuál o cuáles mandamientos NO cumple?'))}")

            st.markdown(f"**Detalles o Comentarios Adicionales:** {mostrar_valor(row.get('Detalles o Comentarios Adicionales'))}")

            st.markdown("---")