# Importación de bibliotecas:
# - Flask: Framework web para crear aplicaciones web en Python.
# - Jinja2: Motor de plantillas integrado en Flask para renderizar HTML dinámico.
# - Pandas y NumPy: Para manipulación y análisis de datos.
# - Requests: Para realizar solicitudes HTTP (en este caso, a la API de GBIF).
# - Folium: Para generar mapas interactivos en HTML.
# - Matplotlib: Para crear gráficos y visualizaciones.
# - Scikit-learn (LinearRegression): Para realizar predicciones basadas en modelos de regresión lineal.
# - Base64 y BytesIO: Para manejar imágenes y gráficos en formato base64.
# - CSV: Para leer archivos CSV.

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import requests
import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import base64
from io import BytesIO
import csv

app = Flask(__name__)  # Flask inicializa la aplicación web.

# Funciones personalizadas:
# - Cargar datos desde archivos CSV y Excel.
# - Consultar datos de especies en la API de GBIF.
# - Crear mapas interactivos con marcadores basados en coordenadas.
# - Realizar predicciones de extinción usando regresión lineal.
# - Generar gráficos y convertirlos a imágenes en base64.

def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    df.set_index("Año", inplace=True)
    return df

def cargar_datos_extintos(nombre_archivo):
    df = pd.read_csv(nombre_archivo, index_col=0).T
    df.index = df.index.astype(int)
    return df

def buscar_en_gbif(nombre_especie):
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={nombre_especie}&limit=50"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get("results", [])
    return []

def crear_mapa_html(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observaciones:
        lat = obs.get("decimalLatitude")
        lon = obs.get("decimalLongitude")
        if lat and lon:
            clima = obtener_datos_climaticos(lat, lon)
            temp = clima['current']['temp'] if clima else "Desconocido"
            folium.Marker(
                location=[lat, lon],
                popup=f"País: {obs.get('country', 'Desconocido')}<br>Temperatura: {temp}°C"
            ).add_to(m)
    return m._repr_html_()

def predecir_año_extincion(df, especie_objetivo, datos_climaticos):
    try:
        X = df.index.values.reshape(-1, 1)
        y = pd.to_numeric(df[especie_objetivo], errors="coerce")
        clima = datos_climaticos.get(especie_objetivo, [])

        # Combinar datos climáticos con años
        if clima:
            X = np.hstack((X, np.array(clima).reshape(-1, 1)))

        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return None, None

        model = LinearRegression().fit(X[mask], y[mask])
        año_ext = -model.intercept_ / model.coef_[0] if model.coef_[0] != 0 else None

        # Generar el gráfico
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(df.index, y, color='orange', label=especie_objetivo)
        if año_ext:
            y_pred = model.predict(X)
            ax.plot(df.index, y_pred, linestyle="--", color="blue", label="Tendencia")
            ax.legend()
            ax.set_xlabel("Año")
            ax.set_ylabel("Población estimada")
            ax.grid()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return int(año_ext) if año_ext else None, img_b64
    except Exception as e:
        print(f"Error en predecir_año_extincion: {e}")
        return None, None

def cargar_datos_especie(nombre_especie):
    with open('c:\\proyecto_especies\\data\\info_especies.csv', encoding='utf-8') as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            if fila['nombre'] == nombre_especie:
                # Validar que las columnas existan y asignar valores predeterminados si están vacías
                return {
                    'nombre_cientifico': fila.get('nombre_cientifico', 'Desconocido'),
                    'estado_conservacion': fila.get('estado', 'Desconocido'),
                    'imagen_especie': fila.get('imagen', 'img/default.jpg'),
                    'acciones_recomendadas': fila.get('acciones_recomendadas', 'No especificado'),
                    'organizaciones': fila.get('organizaciones', 'No especificado'),
                    'amenazas': fila.get('amenazas', 'No especificado')
                }
    return None

def obtener_datos_climaticos(lat, lon):
    api_key = "TU_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Carga de datos:
# - Se cargan datos de especies en peligro desde un archivo CSV.
# - Se cargan datos de especies extintas desde un archivo Excel.
# - Se cargan datos adicionales de especies (como imágenes y descripciones) desde otro archivo CSV.

# - Los datos cargados aquí se utilizan en las rutas de Flask para generar contenido dinámico.

df_monitor = cargar_datos("data/especies_en_peligro.csv")
especies_monitor = df_monitor.columns.tolist()

df_disperso = pd.read_excel("data/especies_extintas.xlsx")
columna_especie = df_disperso.columns[0]
años_excel = pd.to_numeric(df_disperso.columns[1:], errors="coerce").dropna().astype(int)

info_especies = pd.read_csv("data/info_especies.csv")  # ← contiene imagen, nombre, poblacion, estado, etc.

# Rutas de Flask:
# - "/" (index): Página principal.
# - "/blog": Página de blog.
# - "/casos_exito": Página de casos de éxito.
# - "/galeria": Página de galería.
# - "/huella_carbono", "/huella_persona", "/huella_empresa": Páginas relacionadas con la huella de carbono.
# - "/ayudar": Página para mostrar acciones para ayudar.
# - "/refugios": Página de refugios.
# - "/monitorizar": Página para monitorizar especies en peligro.
# - "/especies": Página para consultar información de especies específicas.
# - "/estadisticas/<nombre>": Página para mostrar estadísticas detalladas de una especie.

# - Aquí se definen las rutas de la aplicación web.
# - Flask maneja las solicitudes HTTP y renderiza plantillas HTML con Jinja2.

@app.route("/")
def index():
    # Renderiza la plantilla "index.html" utilizando Jinja2 y así con las demás plantillas
    return render_template("index.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/casos_exito")
def casos_exito():
    return render_template("casos_exito.html")

@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

@app.route("/huella_carbono", methods=["GET", "POST"])
def huella_carbono():
    return render_template("huella_carbono.html")

@app.route("/huella_persona")
def huella_persona():
    return render_template("huella_persona.html")

@app.route("/huella_empresa")
def huella_empresa():
    return render_template("huella_empresa.html")

@app.route("/ayudar")
def acciones():
    return render_template("ayudar.html")

@app.route("/refugios")
def refugios():
    return render_template("refugios.html")

@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    # Renderiza la plantilla "monitorizar.html" y pasa datos dinámicos como:
    # - Lista de especies (`especies`).
    # - Especie seleccionada (`especie`).
    # - Año predicho de extinción (`año_pred`).
    # - Gráfico en base64 (`grafico`).
    # - Mapa interactivo (`mapa`).

    especie_seleccionada = request.form.get("especie") or especies_monitor[0]

    # Manejar el retorno de predecir_año_extincion correctamente
    resultado_prediccion = predecir_año_extincion(df_monitor, especie_seleccionada, {})
    if resultado_prediccion is None or not isinstance(resultado_prediccion, tuple):
        año_pred, grafico_b64 = None, None
    else:
        año_pred, grafico_b64 = resultado_prediccion

    # Procesar las especies para mostrarlas en las tarjetas
    cards = info_especies.to_dict(orient="records")
    for card in cards:
        # Validar que las columnas existan y tengan valores válidos
        card['acciones_recomendadas'] = card.get('acciones_recomendadas', 'No especificado')
        card['organizaciones'] = card.get('organizaciones', 'No especificado')
        card['amenazas'] = card.get('amenazas', 'No especificado')

    # Generar el mapa de observaciones
    observaciones = buscar_en_gbif(especie_seleccionada)
    mapa_html = crear_mapa_html(observaciones)

    return render_template("monitorizar.html",
                           especies=cards,
                           especie=especie_seleccionada,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html)

@app.route("/especies", methods=["GET", "POST"])
def especies():
# Renderiza la plantilla "especies.html" y pasa datos dinámicos como:
    # - Información de la especie (`datos_especie`).
    # - Año predicho de extinción (`año_pred`).
    # - Gráfico en base64 (`grafico`).
    # - Mapa interactivo (`mapa`).
    especie = request.form.get("especie")
    datos_especie = None
    mapa_html = None
    grafico_b64 = None
    año_ext = None

    if especie:
        registros = buscar_en_gbif(especie)
        datos_especie = registros[:50] if registros else []

        df_fila = df_disperso[df_disperso[columna_especie] == especie]
        if not df_fila.empty:
            fila = df_fila.iloc[0]
            y = pd.to_numeric(fila[1:].values, errors="coerce")
            X = años_excel.values.reshape(-1, 1)
            mask = ~np.isnan(y)

            if mask.sum() >= 2:
                modelo = LinearRegression().fit(X[mask], y[mask])
                año_ext = -modelo.intercept_ / modelo.coef_[0] if modelo.coef_[0] != 0 else None

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.scatter(años_excel, y, color='orange', label=especie)
                ax.plot(años_excel, modelo.predict(X), linestyle="--", color="blue")
                ax.set_xlabel("Año")
                ax.set_ylabel("Población")
                ax.set_title("Evolución poblacional")
                ax.grid()
                ax.legend()

                buf = BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                grafico_b64 = base64.b64encode(buf.read()).decode("utf-8")
                plt.close(fig)

            mapa_html = crear_mapa_html(registros)

    return render_template("especies.html",
                           especie=especie,
                           año_pred=año_ext,
                           grafico=grafico_b64,
                           mapa=mapa_html,
                           datos=datos_especie)

@app.route("/estadisticas/<nombre>")
def estadisticas(nombre):
    # Renderiza la plantilla "estadisticas.html" y pasa datos dinámicos como:
    # - Nombre de la especie (`especie`).
    # - Año predicho de extinción (`año_pred`).
    # - Gráfico en base64 (`grafico`).
    # - Mapa interactivo (`mapa`).
    # - Información adicional de la especie (usando `**datos_especie`).
    datos_especie = cargar_datos_especie(nombre)
    if not datos_especie:
        return "Especie no encontrada", 404

    # Manejar el retorno de predecir_año_extincion correctamente
    resultado_prediccion = predecir_año_extincion(df_monitor, nombre, {})
    if resultado_prediccion is None or not isinstance(resultado_prediccion, tuple):
        año_pred, grafico_b64 = None, None
    else:
        año_pred, grafico_b64 = resultado_prediccion

    # Buscar observaciones en GBIF y generar el mapa
    registros = buscar_en_gbif(nombre)
    mapa_html = crear_mapa_html(registros)

    return render_template("estadisticas.html",
                           especie=nombre,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html,
                           **datos_especie)

# Ejecución de la aplicación Flask en modo debug.
if __name__ == "__main__":
    app.run(debug=True)