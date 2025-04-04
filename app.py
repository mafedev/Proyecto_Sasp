import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Dashboard de Extinción de Especies con IA")

# ===================== 📥 Cargar archivo Excel =====================
@st.cache_data
def cargar_datos_excel(nombre_archivo):
    if nombre_archivo.endswith(".xlsx"):
        df = pd.read_excel(nombre_archivo)
    else:
        df = pd.read_csv(nombre_archivo)
    columnas_años = df.columns[1:]
    años = pd.to_numeric(columnas_años, errors='coerce').dropna().astype(int)
    return df, años

archivo_excel = "especies_disperso.xlsx"
df_excel, años_excel = cargar_datos_excel(archivo_excel)

# Detectar dinámicamente la columna con los nombres de especie
columna_especie = df_excel.columns[0]

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
def predecir_año_extincion(df, años, especie_objetivo, columna_nombre):
    X = []
    y = []
    for i in range(len(df)):
        poblacion = df.iloc[i, 1:].values
        años_validos = años[~pd.isna(poblacion)]
        poblacion_validos = poblacion[~pd.isna(poblacion)]
        for a, p in zip(años_validos, poblacion_validos):
            X.append([a])
            y.append(p)
    model = LinearRegression()
    model.fit(X, y)

    if especie_objetivo in df[columna_nombre].values:
        st.success("📌 Esta especie ya está extinta. Mostrando gráfico de su descenso poblacional...")
        return None, model
    else:
        año_predicho = int(-model.intercept_ / model.coef_[0])
        return año_predicho, model

# ===================== 🎯 Interfaz Principal =====================
especie_usuario = st.text_input("🔍 Ingrese el nombre científico de una especie:", "Panthera onca")

if st.button("Buscar especie"):
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

        # 📈 Diagrama de dispersión
    st.subheader("📉 Evolución poblacional")
    fig, ax = plt.subplots(figsize=(8, 5))

    if especie_usuario in df_excel[columna_especie].values:
        fila = df_excel[df_excel[columna_especie] == especie_usuario].iloc[0]
        poblacion = pd.to_numeric(fila[1:].values, errors="coerce")  # 🔹 CORRECCIÓN
        ax.scatter(años_excel, poblacion, color='orange', label=especie_usuario)

        modelo = LinearRegression()
        modelo.fit(años_excel.values.reshape(-1, 1), poblacion)
        y_pred = modelo.predict(años_excel.values.reshape(-1, 1))
        ax.plot(años_excel, y_pred, color='blue', linestyle='--', label="Ajuste lineal")
    else:
        for i in range(len(df_excel)):
            especie = df_excel.iloc[i, 0]
            valores = pd.to_numeric(df_excel.iloc[i, 1:].values, errors="coerce")  # 🔹 CORRECCIÓN
            valid = ~np.isnan(valores)  # 🔹 AHORA FUNCIONA
            ax.scatter(años_excel[valid], valores[valid], alpha=0.3)

        # Ajuste general
        X_all = []
        y_all = []
        for i in range(len(df_excel)):
            valores = pd.to_numeric(df_excel.iloc[i, 1:].values, errors="coerce")  # 🔹 CORRECCIÓN
            valid = ~np.isnan(valores)
            X_all += list(años_excel[valid])
            y_all += list(valores[valid])

        modelo = LinearRegression()
        modelo.fit(np.array(X_all).reshape(-1, 1), y_all)
        y_pred = modelo.predict(np.array(años_excel).reshape(-1, 1))
        ax.plot(años_excel, y_pred, color='red', linestyle='--', label="Tendencia global")

    ax.set_xlabel("Año")
    ax.set_ylabel("Población estimada")
    ax.set_title("Diagrama de dispersión")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 🔮 Predicción de año de extinción
    año_predicho, _ = predecir_año_extincion(df_excel, años_excel, especie_usuario, columna_especie)
    if año_predicho:
        st.info(f"🧠 **Predicción de año estimado de extinción para {especie_usuario}: {año_predicho}**")
