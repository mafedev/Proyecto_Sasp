# Importación de bibliotecas:

# - Jinja2: Motor de plantillas integrado en Flask para renderizar HTML dinámico.

from flask import Flask, render_template, request # Framework web para crear aplicaciones web en Python
import pandas as pd # Pandas y NumPy: Para manipulación y análisis de datos.
import numpy as np 
import requests # Para realizar solicitudes HTTP (en este caso, a la API de GBIF)
import folium # Folium: Para generar mapas interactivos en HTML
import matplotlib # Para crear gráficos y visualizaciones
matplotlib.use("Agg") # Configura matplotlib para no usar la interfaz gráfica, porque da problemas
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression # Regresión lineal para predecir el año de extinción
import base64 # Para codificar imágenes en base64, es decir, convertir imágenes a texto para poder enviarlas por HTTP

from io import BytesIO # ----- comprobarlo luego
import csv
import urllib.parse  # Para codificar correctamente los nombres de las especies

# Se inicializa la aplicación web
app = Flask(__name__)

# FUNCIONES
# Carga un csv y lo convierte a un dataframe de pandas, establece la columna "Año" como índice
def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo) # Carga el archivo CSV
    df.set_index("Año", inplace=True) # Establece la columna "Año" como índice
    return df # Devuelve el dataframe

# Carga un csv, intercambia las filas con las columnas y convierte el índice a entero
def cargar_datos_extintos(nombre_archivo):
    df = pd.read_csv(nombre_archivo, index_col=0).T # Carga el archivo e intercambia filas y columnas
    df.index = df.index.astype(int) # Convierte el índice a entero
    return df

# Busca en la API de GBIF usando el nombre científico de la especie y devuelve los resultados
def buscar_en_gbif(nombre_especie):
    # Primero intenta buscar el nombre completo usando el parámetro `q` para coincidencias amplias
    nombre_especie_codificado = urllib.parse.quote(nombre_especie)
    url = f"https://api.gbif.org/v1/occurrence/search?q={nombre_especie_codificado}&limit=50"
    r = requests.get(url)
    if r.status_code == 200:
        resultados = r.json().get("results", [])
        if resultados:  # Si encuentra resultados con el nombre completo, los devuelve
            return resultados

    # Si no encuentra resultados, intenta buscar con cada palabra del nombre
    palabras = nombre_especie.split()
    for palabra in palabras:
        nombre_especie_codificado = urllib.parse.quote(palabra)
        url = f"https://api.gbif.org/v1/occurrence/search?q={nombre_especie_codificado}&limit=50"
        r = requests.get(url)
        if r.status_code == 200:
            resultados = r.json().get("results", [])
            if resultados:  # Si encuentra resultados con una palabra, los devuelve
                return resultados

    return []  # Si no encuentra nada, devuelve una lista vacía

# Crea un mapa HTML usando Folium y coloca marcadores para cada observación de la especie
def crear_mapa_html(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=3) # Crea un mapa centrado en el ecuador y con un zoom inicial de 3
    for obs in observaciones: # Itera sobre cada observación
        lat = obs.get("decimalLatitude") # Obtiene la latitud de la observación
        lon = obs.get("decimalLongitude") # Obtiene la longitud de la observación
        if lat and lon: # Verifica si la latitud y longitud son válidas
            folium.Marker(
                location=[lat, lon],
                popup=f"País: {obs.get('country', 'Desconocido')}"
            ).add_to(m)
    return m._repr_html_()

def predecir_año_extincion(df, especie_objetivo):
    try:
        X = df.index.values.reshape(-1, 1)
        y = pd.to_numeric(df[especie_objetivo], errors="coerce")

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
    especie_seleccionada = request.form.get("especie") or especies_monitor[0]

    # Manejar el retorno de predecir_año_extincion correctamente
    resultado_prediccion = predecir_año_extincion(df_monitor, especie_seleccionada)
    if resultado_prediccion is None or not isinstance(resultado_prediccion, tuple):
        año_pred, grafico_b64 = None, None
    else:
        año_pred, grafico_b64 = resultado_prediccion

    # Procesar las especies para mostrarlas en las tarjetas
    cards = info_especies.to_dict(orient="records")
    for card in cards:
        card['acciones_recomendadas'] = card.get('acciones_recomendadas', 'No especificado')
        card['organizaciones'] = card.get('organizaciones', 'No especificado')
        card['amenazas'] = card.get('amenazas', 'No especificado')

    # Generar el mapa de observaciones
    observaciones = buscar_en_gbif(especie_seleccionada)
    mapa_html = crear_mapa_html(observaciones)  # Genera el mapa

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
    resultado_prediccion = predecir_año_extincion(df_monitor, nombre)
    if resultado_prediccion is None or not isinstance(resultado_prediccion, tuple):
        año_pred, grafico_b64 = None, None
    else:
        año_pred, grafico_b64 = resultado_prediccion

    # Buscar observaciones en GBIF y generar el mapa
    registros = buscar_en_gbif(nombre)
    mapa_html = crear_mapa_html(registros)  # Generar el mapa directamente

    return render_template("estadisticas.html",
                           especie=nombre,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html,
                           **datos_especie)

# Ejecución de la aplicación Flask en modo debug.
if __name__ == "__main__":
    app.run(debug=True)