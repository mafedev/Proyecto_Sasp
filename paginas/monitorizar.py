import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Se asegura que la variable de sesión "pagina_actual" esté inicializada
def mostrar(ir_a):
    st.header("🐾 Monitorización de Especies en Peligro")

    # Cargar datos desde un archivo CSV
    @st.cache_data
    def cargar_datos_csv(nombre_archivo):
        return pd.read_csv(nombre_archivo)

    
    # Cargar el archivo CSV con los datos de especies en peligro
    # Se asegura que el archivo CSV esté en la misma carpeta que este script
    df = cargar_datos_csv("data/especies_en_peligro.csv")
    df.set_index("Año", inplace=True) # Establece la columna "Año" como índice
    especies = df.columns.tolist()

    st.sidebar.subheader("📌 Especies disponibles")
    for especie in especies:
        if st.sidebar.button(especie, key=f"btn_{especie}"):
            st.session_state["especie_usuario"] = especie


    if "especie_usuario" not in st.session_state:
        st.session_state["especie_usuario"] = especies[0]

    especie_usuario = st.text_input("🔍 Ingrese el nombre científico de una especie:", st.session_state["especie_usuario"])
    st.session_state["especie_usuario"] = especie_usuario

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

    def predecir_año_extincion(df, especie_objetivo):
        X = df.index.values.reshape(-1, 1)
        y = pd.to_numeric(df[especie_objetivo], errors="coerce")
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return None, None
        model = LinearRegression().fit(X[mask], y[mask])
        if model.coef_[0] == 0:
            return None, model
        año_ext = -model.intercept_ / model.coef_[0]
        return int(año_ext), model

    if especie_usuario in especies:
        st.subheader(f"🔎 Resultados para: {especie_usuario}")
        registros = buscar_en_gbif(especie_usuario)
        if registros:
            st.success(f"✅ {len(registros)} registros encontrados en GBIF")
            df_gbif = pd.DataFrame([
                {"País": r.get("country"), "Lat": r.get("decimalLatitude"), "Lon": r.get("decimalLongitude")}
                for r in registros if r.get("decimalLatitude") and r.get("decimalLongitude")
            ])
            col1, col2 = st.columns(2)
            with col1:
                folium_static(crear_mapa(registros))
            with col2:
                st.plotly_chart(px.scatter_geo(df_gbif, lat="Lat", lon="Lon", title="Distribución Geográfica"))

        st.subheader("📉 Evolución Poblacional")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(df.index, df[especie_usuario], color='orange', label=especie_usuario)
        año_pred, modelo = predecir_año_extincion(df, especie_usuario)
        if año_pred:
            y_pred = modelo.predict(df.index.values.reshape(-1, 1))
            ax.plot(df.index, y_pred, linestyle="--", color="blue", label="Tendencia")
            st.info(f"🧠 **Posible extinción en el año: {año_pred}**")
            if año_pred - 2024 <= 10:
                st.error("⚠️ Riesgo crítico: extinción en menos de 10 años.")
        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.legend()
        ax.grid()
        st.pyplot(fig)
