import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import folium
from streamlit_folium import folium_static
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Dashboard de Extinción de Especies con IA")

# ===================== 📥 Cargar archivo CSV =====================
@st.cache_data
def cargar_datos_csv(nombre_archivo):
    df = pd.read_csv(nombre_archivo)  # Cargar CSV
      # Usar la columna "Especie" como índice
    return df

archivo_csv = "especies_en_peligro.csv"
df_especies = cargar_datos_csv(archivo_csv)

# Lista de especies disponibles
especies_disponibles = df_especies.columns.tolist()
st.sidebar.subheader("📌 Especies disponibles")
st.sidebar.write(especies_disponibles)

# ===================== 🔍 Búsqueda en GBIF =====================
def buscar_en_gbif(nombre_especie):
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={nombre_especie}&limit=50"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get("results", [])
    return []

def crear_mapa(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observaciones:
        lat = obs.get("decimalLatitude")
        lon = obs.get("decimalLongitude")
        if lat and lon:
            folium.Marker(location=[lat, lon], popup=obs.get("country", "Observación")).add_to(m)
    return m

# ===================== 🔢 IA: Predicción de año de extinción =====================
def predecir_año_extincion(df, especie_objetivo):
    X = df.index.values.reshape(-1, 1)
    y = df[especie_objetivo].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    año_predicho = int(-model.intercept_ / model.coef_[0])
    return año_predicho, model

# ===================== 🎯 Interfaz Principal =====================
especie_usuario = st.text_input("🔍 Ingrese el nombre científico de una especie:", "Especie_1")

if especie_usuario in especies_disponibles:
    st.subheader(f"🔎 Resultados para: {especie_usuario}")

    # 📊 Mapa de registros desde GBIF
    registros = buscar_en_gbif(especie_usuario)
    if registros:
        st.success(f"✅ Se encontraron {len(registros)} registros en GBIF")
        df_gbif = pd.DataFrame([
            {"País": r.get("country"), "Lat": r.get("decimalLatitude"), "Lon": r.get("decimalLongitude")}
            for r in registros if r.get("decimalLatitude") and r.get("decimalLongitude")
        ])
        col1, col2 = st.columns(2)
        with col1:
            folium_static(crear_mapa(registros))
        with col2:
            st.plotly_chart(px.scatter_geo(df_gbif, lat="Lat", lon="Lon", title="Distribución Geográfica"))
    else:
        st.warning("⚠️ No se encontraron registros en GBIF.")

    # 📈 Gráfico de evolución poblacional
    st.subheader("📉 Evolución Poblacional de la Especie")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_especies.index, df_especies[especie_usuario], color='orange', label=especie_usuario)
    
    año_predicho, modelo = predecir_año_extincion(df_especies, especie_usuario)
    y_pred = modelo.predict(df_especies.index.values.reshape(-1, 1))
    ax.plot(df_especies.index, y_pred, color='blue', linestyle='--', label="Tendencia")
    
    ax.set_xlabel("Año")
    ax.set_ylabel("Población estimada")
    ax.set_title("Diagrama de Dispersión y Tendencia")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
    # 🔮 Predicción de extinción
    st.info(f"🧠 **Predicción de extinción para {especie_usuario}: {año_predicho}**")
    
    años_restantes = año_predicho - 2024
    if años_restantes <= 10:
        st.error(f"⚠️ ¡Alerta! {especie_usuario} podría extinguirse en menos de 10 años.")
else:
    st.warning("⚠️ La especie ingresada no está en la base de datos. Pruebe con otra.")
