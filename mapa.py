# pip install streamlit requests folium streamlit-folium plotly pandas
import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px

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

def create_map(observations):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observations:
        lat = obs["geojson"]["coordinates"][1]
        lon = obs["geojson"]["coordinates"][0]
        folium.Marker(location=[lat, lon], popup=obs["species_guess"]).add_to(m)
    return m

st.title("🌍 Dashboard de Observaciones y Estado de Conservación de Especies")
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
