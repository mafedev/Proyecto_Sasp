import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import plotly.express as px

# Llamado de la función para mostrar la página de búsqueda de especies
def mostrar(ir_a):
    st.header("🔬 Buscar especie en base de datos dispersa")

    @st.cache_data
    def cargar_datos_excel(nombre_archivo):
        df = pd.read_excel(nombre_archivo) if nombre_archivo.endswith(".xlsx") else pd.read_csv(nombre_archivo)
        años = pd.to_numeric(df.columns[1:], errors="coerce").dropna().astype(int)
        return df, años

    df_excel, años_excel = cargar_datos_excel("data/especies_disperso.xlsx")
    columna_especie = df_excel.columns[0]

    especie_usuario = st.text_input("🔍 Ingrese el nombre científico de una especie:", "Panthera onca")

    # Busca la especie en GBIF y devuelve los registros encontrados
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
    # 
    def predecir_año_extincion(df, años, especie, col_nombre):
        if especie not in df[col_nombre].values:
            return None, None
        fila = df[df[col_nombre] == especie].iloc[0]
        y = pd.to_numeric(fila[1:].values, errors="coerce")
        X = años.values.reshape(-1, 1)
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return None, None
        modelo = LinearRegression().fit(X[mask], y[mask])
        if modelo.coef_[0] == 0:
            return None, modelo
        año_ext = -modelo.intercept_ / modelo.coef_[0]
        return int(año_ext), modelo

    if st.button("Buscar especie"):
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

        if especie_usuario in df_excel[columna_especie].values:
            fila = df_excel[df_excel[columna_especie] == especie_usuario].iloc[0]
            poblacion = pd.to_numeric(fila[1:].values, errors="coerce")
            ax.scatter(años_excel, poblacion, color='orange', label=especie_usuario)
            modelo = LinearRegression().fit(años_excel.values.reshape(-1, 1), poblacion)
            ax.plot(años_excel, modelo.predict(años_excel.values.reshape(-1, 1)), color='blue', linestyle='--')
        else:
            for i in range(len(df_excel)):
                valores = pd.to_numeric(df_excel.iloc[i, 1:].values, errors="coerce")
                valid = ~np.isnan(valores)
                ax.scatter(años_excel[valid], valores[valid], alpha=0.3)
            X_all, y_all = [], []
            for i in range(len(df_excel)):
                valores = pd.to_numeric(df_excel.iloc[i, 1:].values, errors="coerce")
                valid = ~np.isnan(valores)
                X_all += list(años_excel[valid])
                y_all += list(valores[valid])
            modelo = LinearRegression().fit(np.array(X_all).reshape(-1, 1), y_all)
            ax.plot(años_excel, modelo.predict(np.array(años_excel).reshape(-1, 1)), color='red', linestyle='--')

        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.set_title("Diagrama de dispersión")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        año_predicho, _ = predecir_año_extincion(df_excel, años_excel, especie_usuario, columna_especie)
        if año_predicho:
            st.info(f"🧠 **Año estimado de extinción: {año_predicho}**")
