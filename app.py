import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
import numpy as np

def get_inat_data(species_name):
    url = f"https://api.inaturalist.org/v1/observations?taxon_name={species_name}&per_page=50"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_iucn_status(species_name, api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/species/{species_name}?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and data['result']:
            return data['result'][0]['category']
    return "Desconocido"

def get_pollution_data():
    url = "https://api.openaq.org/v1/latest?country=US&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results'][0]['measurements'][0]['value']  # Valor de contaminación
    return None

def create_map(observations):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observations:     
        lat = obs["geojson"]["coordinates"][1]
        lon = obs["geojson"]["coordinates"][0]
        folium.Marker(location=[lat, lon], popup=obs["species_guess"]).add_to(m)
    return m

def predict_extinction_risk(pollution, habitat_loss, hunting):
    model = RandomForestClassifier()
    X_train = np.array([[30, 50, 70], [10, 20, 30], [70, 80, 90]])  # Datos ficticios
    y_train = np.array([1, 0, 1])  # 1 = en peligro, 0 = no en peligro
    model.fit(X_train, y_train)
    prediction = model.predict([[pollution, habitat_loss, hunting]])
    return "Alto" if prediction[0] == 1 else "Bajo"

st.title("🌍 Dashboard de Extinción de Especies")
species_name = st.text_input("🔍 Ingrese el nombre científico de la especie:", "Panthera onca")
api_key = st.text_input("🔑 Ingrese su API Key de IUCN:", type="password")

if st.button("Buscar"):
    st.write(f"🔎 Buscando datos para: {species_name}...")
    
    inat_data = get_inat_data(species_name)
    if inat_data:
        observations = inat_data["results"]
        st.success(f"✅ Se encontraron {len(observations)} observaciones en iNaturalist.")
        
        df = pd.DataFrame([
            {"Latitud": obs["geojson"]["coordinates"][1], "Longitud": obs["geojson"]["coordinates"][0]} 
            for obs in observations if "geojson" in obs
        ])
        
        st.write("📍 Mapa de Observaciones:")
        folium_static(create_map(observations))
        
        st.write("📊 Distribución Geográfica:")
        fig = px.scatter_geo(df, lat="Latitud", lon="Longitud", title="Observaciones Globales")
        st.plotly_chart(fig)
    else:
        st.error("⚠️ No se encontraron observaciones en iNaturalist.")
    
    if api_key:
        status = get_iucn_status(species_name, api_key)
        st.write(f"🛑 Estado de conservación según IUCN: **{status}**")
    else:
        st.warning("⚠️ Ingrese una API Key de IUCN para obtener el estado de conservación.")
    
    pollution = get_pollution_data() or 50  # Valor por defecto si falla la API
    habitat_loss = np.random.randint(20, 80)  # Simulación
    hunting = np.random.randint(10, 60)  # Simulación
    
    st.write("📊 Factores de Extinción:")
    factors_df = pd.DataFrame({"Factor": ["Contaminación", "Pérdida de Hábitat", "Caza"],
                               "Valor": [pollution, habitat_loss, hunting]})
    st.bar_chart(factors_df.set_index("Factor"))
    
    risk = predict_extinction_risk(pollution, habitat_loss, hunting)
    st.write(f"🔮 **Predicción de Riesgo de Extinción: {risk}**")