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

# ----------------------- Estado inicial -----------------------
if "pagina_actual" not in st.session_state:
    st.session_state["pagina_actual"] = "Inicio"

# ----------------------- Navegación -----------------------
def ir_a(pagina):
    st.session_state["pagina_actual"] = pagina

# ----------------------- Pantalla de inicio -----------------------
if st.session_state["pagina_actual"] == "Inicio":
    st.header("🌱 Bienvenido al Observatorio Global de Especies en Peligro")
    st.markdown("""
    Este dashboard utiliza datos abiertos y algoritmos de Inteligencia Artificial para:
    - 📊 Monitorizar poblaciones de especies en riesgo.
    - 🔍 Explorar especies mediante sus registros geográficos.
    - 💼 Conectar con iniciativas de conservación y empresas comprometidas.

    Selecciona una opción para continuar:
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐾 Monitorizar especies en peligro"):
            ir_a("Monitorizar")
    with col2:
        if st.button("🔬 Buscar especie"):
            ir_a("Buscar")
    with col3:
        if st.button("🏢 Empresas"):
            ir_a("Empresas")

# ----------------------- Sección: Monitorizar -----------------------
elif st.session_state["pagina_actual"] == "Monitorizar":
    st.header("🐾 Monitorización de Especies en Peligro")

    @st.cache_data
    def cargar_datos_csv(nombre_archivo):
        return pd.read_csv(nombre_archivo)

    df = cargar_datos_csv("especies_en_peligro.csv")
    df.set_index("Año", inplace=True)
    especies = df.columns.tolist()

    st.sidebar.subheader("📌 Especies disponibles")
    for especie in especies:
        if st.sidebar.button(especie):
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

# ----------------------- Sección: Buscar especie -----------------------
elif st.session_state["pagina_actual"] == "Buscar":
    st.header("🔬 Buscar especie en base de datos dispersa")

    @st.cache_data
    def cargar_datos_excel(nombre_archivo):
        df = pd.read_excel(nombre_archivo) if nombre_archivo.endswith(".xlsx") else pd.read_csv(nombre_archivo)
        años = pd.to_numeric(df.columns[1:], errors="coerce").dropna().astype(int)
        return df, años

    df_excel, años_excel = cargar_datos_excel("especies_disperso.xlsx")
    columna_especie = df_excel.columns[0]

    especie_usuario = st.text_input("🔍 Ingrese el nombre científico de una especie:", "Panthera onca")
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

# ----------------------- Sección: Empresas -----------------------
elif st.session_state["pagina_actual"] == "Empresas":
    st.header("🏢 Sección de Empresas")
    st.info("Aquí se mostrarán iniciativas empresariales relacionadas con la conservación. (En construcción)")

# ----------------------- Botón de volver -----------------------
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al inicio"):
    ir_a("Inicio")