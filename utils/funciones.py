import pandas as pd
import numpy as np
import requests
import folium
import matplotlib
matplotlib.use("Agg")  # ← Forza uso de backend sin GUI
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import base64
from io import BytesIO

# Carga el CSV y pone "Año" como índice
def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    df.set_index("Año", inplace=True)
    return df

# Llama a la API de GBIF para buscar ocurrencias de la especie
def buscar_en_gbif(nombre_especie):
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={nombre_especie}&limit=50"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get("results", [])
    return []

# Crea un mapa con los registros y lo devuelve como HTML
def crear_mapa_html(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observaciones:
        lat = obs.get("decimalLatitude")
        lon = obs.get("decimalLongitude")
        if lat and lon:
            folium.Marker(location=[lat, lon], popup=obs.get("country", "Observación")).add_to(m)
    return m._repr_html_()  # Devuelve HTML para insertar en plantilla

# Predice el año de extinción y genera el gráfico como imagen base64
def predecir_año_extincion(df, especie_objetivo):
    X = df.index.values.reshape(-1, 1)
    y = pd.to_numeric(df[especie_objetivo], errors="coerce")

    # Filtra valores válidos
    mask = ~np.isnan(y)
    if mask.sum() < 2:
        return None, None

    # Ajusta modelo de regresión lineal
    model = LinearRegression().fit(X[mask], y[mask])
    año_ext = -model.intercept_ / model.coef_[0] if model.coef_[0] != 0 else None

    # Crea gráfico con matplotlib
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(df.index, y, color='orange', label=especie_objetivo)
    if año_ext:
        y_pred = model.predict(X)
        ax.plot(df.index, y_pred, linestyle="--", color="blue", label="Tendencia")
        ax.legend()
        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.grid()

    # Convierte la figura a imagen en base64 para insertar en HTML
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    return int(año_ext) if año_ext else None, img_b64

# Carga y transforma el CSV de especies extintas (donde los años están como columnas)
def cargar_datos_extintos(nombre_archivo):
    df = pd.read_csv(nombre_archivo, index_col=0).T  # Transpone: ahora los años serán las filas (index)
    df.index = df.index.astype(int)  # Asegura que los años sean números
    return df
