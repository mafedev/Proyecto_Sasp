from flask import Flask, render_template, request, redirect, url_for # Se importa Flask, render_template para renderizar los template, request para manejar las solicitudes HTTP, redirect y url_for para redirigir a otras rutas
import os # Para rutas de archivos
import pandas as pd # Para manejar datos en formato CSV y Excel
import numpy as np # Para operaciones numéricas
import requests # Para hacer solicitudes HTTP a la API de GBIF
import folium # Para crear mapas interactivos
import matplotlib # Para crear gráficos
matplotlib.use("Agg") # Para evitar problemas con la interfaz gráfica en servidores sin pantalla
import matplotlib.pyplot as plt
import base64 # Para codificar imágenes en base64, es decir, convertir imágenes a texto para poder enviarlas por HTTP
from io import BytesIO # Para las gráficas
import csv # Para manejar archivos CSV
import urllib.parse # Para trabajar con URLs
from modelo import predecir_nn, obtener_df_extintas #Funciones de modelo.py para predecir la probabilidad de extinción usando una red neuronal y obtener el DataFrame de especies extintas

# Inicializar la aplicación Flask
app = Flask(__name__)

# Rutas de Flask
@app.route("/")
def index():
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

# Ruta para la página de monitorización, donde se selecciona una especie y se muestra información sobre ella
@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    especie_seleccionada = request.form.get("especie") or especies_monitor[0] # Si no se selecciona ninguna especie, se toma la primera de la lista
    resultado_prediccion = predecir_año_extincion(df_monitor, especie_seleccionada) # Se llama a la función de predicción de año de extinción
    if resultado_prediccion is None or not isinstance(resultado_prediccion, tuple): 
        año_pred, grafico_b64 = None, None # Si no se obtiene un resultado válido, se les asigna none
    else:
        año_pred, grafico_b64 = resultado_prediccion # Si se obtiene un resultado válido, se asigna el año de predicción y el gráfico en base64

    cards = info_especies.to_dict(orient="records") # Se convierte el DataFrame de información de especies a una lista de diccionarios
    for card in cards: # Se itera sobre cada especie para agregar información adicional
        card['acciones_recomendadas'] = card.get('acciones_recomendadas', 'No especificado') 
        card['organizaciones'] = card.get('organizaciones', 'No especificado')
        card['amenazas'] = card.get('amenazas', 'No especificado')

    observaciones = buscar_en_gbif(especie_seleccionada) # Se buscan observaciones de la especie seleccionada en la API de GBIF
    mapa_html = crear_mapa_html(observaciones) # Se crea un mapa HTML con las observaciones

    # Se devuelve la plantilla monitorizar.html con la información de las especies, la especie seleccionada, el año de predicción, el gráfico y el mapa
    return render_template("monitorizar.html",
                           especies=cards,
                           especie=especie_seleccionada,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html)

# Ruta para la página de estadísticas de una especie específica, se muestra al seleccionar una especie en monitorizar
@app.route("/estadisticas/<nombre>", methods=["GET", "POST"])  # Se define la ruta con el nombre de la especie como parámetro
def estadisticas(nombre):
    datos_especie = cargar_datos_especie(nombre)  # Se carga la información de la especie desde el archivo CSV
    if not datos_especie:  # Si no se encuentra la especie, muestra un mensaje de error
        return "Especie no encontrada", 404

    metodo = request.form.get("metodo", "lineal")  # Se obtiene el método de predicción seleccionado (lineal o red neuronal), por defecto es lineal
    año_pred = None
    grafico_b64 = None
    probabilidad_nn = None
    reubicacion = None  # Inicializar variable para la reubicación

    poblacion_historica = []  # Inicializa la lista de población histórica
    if nombre in df_monitor.columns:  # Verifica si la especie está en el DataFrame de monitoreo
        especie_serie = df_monitor[nombre].dropna()
        poblacion_historica = list(zip(especie_serie.index, especie_serie.values))

    if metodo == "lineal":  # Si el método seleccionado es lineal, se llama a la función de predicción de año de extinción
        año_pred, grafico_b64 = predecir_año_extincion(df_monitor, nombre)
    elif metodo == "red_neuronal":  # Si el método seleccionado es red neuronal, se llama a la función de predicción de la red neuronal
        print("Método seleccionado:", metodo)
        probabilidad_nn = predecir_nn(nombre)  # Se obtiene la probabilidad de extinción de la especie
        if probabilidad_nn is None:  # Si no se obtiene un resultado válido, se asigna None
            print(f"No se pudo realizar la predicción para la especie: {nombre}")

    tendencia_reciente = verificar_tendencia_reciente(df_monitor, nombre)

    # Si la tendencia es decreciente, obtener la información de reubicación
    if tendencia_reciente == "Decremento":
        reubicacion = datos_especie.get("reubicacion", "No hay recomendaciones de reubicación disponibles.")

    registros = buscar_en_gbif(nombre)
    mapa_html = crear_mapa_html(registros)

    return render_template("estadisticas.html",
                           especie=nombre,
                           imagen_especie=datos_especie.get("imagen_especie"),
                           descripcion=datos_especie.get("descripcion"),
                           nombre_cientifico=datos_especie.get("nombre_cientifico"),
                           habitat=datos_especie.get("habitat"),
                           amenazas=datos_especie.get("amenazas"),
                           poblacion_historica=poblacion_historica,
                           mapa=mapa_html,
                           grafico=grafico_b64 if metodo == "lineal" else None,
                           año_pred=año_pred,
                           acciones_recomendadas=datos_especie.get("acciones_recomendadas"),
                           organizaciones=datos_especie.get("organizaciones"),
                           tendencia_reciente=tendencia_reciente,
                           metodo=metodo,
                           probabilidad_nn=probabilidad_nn,
                           reubicacion=reubicacion)


# Funciones auxiliares
def cargar_info_conservacion():
    ruta_archivo = 'data/info_modelo.csv'
    if ruta_archivo.endswith('.xlsx'):
        return pd.read_excel(ruta_archivo)
    else:
        return pd.read_csv(ruta_archivo)

def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    df.set_index("Año", inplace=True)
    return df

def cargar_datos_especie(nombre_especie):
    with open('c:\\proyecto_especies\\data\\info_especies.csv', encoding='utf-8') as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            if fila['nombre'] == nombre_especie:
                return {
                    'nombre_cientifico': fila.get('nombre_cientifico', 'Desconocido'),
                    'estado_conservacion': fila.get('estado', 'Desconocido'),
                    'imagen_especie': fila.get('imagen', 'img/default.jpg'),
                    'acciones_recomendadas': fila.get('acciones_recomendadas', 'No especificado'),
                    'organizaciones': fila.get('organizaciones', 'No especificado'),
                    'amenazas': fila.get('amenazas', 'No especificado'),
                    'descripcion': fila.get('descripcion', 'Descripción no disponible'),
                    'habitat': fila.get('habitat', 'Hábitat no disponible'),
                    'reubicacion': fila.get('reubicacion', 'No hay recomendaciones de reubicación disponibles.')
                }
    return None

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


def crear_mapa_html(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=3)
    for obs in observaciones:
        lat = obs.get("decimalLatitude")
        lon = obs.get("decimalLongitude")
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"País: {obs.get('country', 'Desconocido')}"
            ).add_to(m)
    return m._repr_html_()

def predecir_año_extincion(df, especie):
    try:
        anios = df.index.values.astype(float)
        poblacion = pd.to_numeric(df[especie], errors="coerce").values
        datos_validos = ~np.isnan(poblacion)
        anios = anios[datos_validos]
        poblacion = poblacion[datos_validos]

        if len(anios) < 2:
            return None, None

        promedio_anios = np.mean(anios)
        promedio_poblacion = np.mean(poblacion)
        numerador = np.sum((anios - promedio_anios) * (poblacion - promedio_poblacion))
        denominador = np.sum((anios - promedio_anios) ** 2)

        if denominador == 0:
            return None, None

        pendiente = numerador / denominador
        intercepto = promedio_poblacion - pendiente * promedio_anios

        if pendiente == 0:
            return None, None

        anio_extincion = -intercepto / pendiente

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(anios, poblacion, color='orange', label=especie)
        poblacion_estim = pendiente * anios + intercepto
        ax.plot(anios, poblacion_estim, linestyle="--", color="blue", label="Tendencia")
        ax.legend()
        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.grid()

        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)

        return int(anio_extincion) if anio_extincion > 0 else None, imagen_base64

    except Exception as error:
        print(f"Error en predecir_año_extincion: {error}")
        return None, None

def verificar_tendencia_reciente(df, especie):
    try:
        # Convertir a números y eliminar valores nulos
        datos = df[especie].astype(float).dropna()

        if len(datos) < 10:
            return "No hay suficientes datos para evaluar 10 años"

        # Tomar los últimos 10 datos
        ultimos = datos[-10:]

        # Crear valores para X
        x = np.arange(len(ultimos))
        y = ultimos.values

        # Calcular regresión lineal manual
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        numerador = np.sum((x - x_mean) * (y - y_mean))
        denominador = np.sum((x - x_mean) ** 2)
        pendiente = numerador / denominador if denominador != 0 else 0

        # Evaluar la tendencia
        if pendiente > 0:
            return "Incremento"
        elif pendiente < 0:
            return "Decremento"
        else:
            return "Estable"

    except:
        return "Error en los datos"


# Cargar datos iniciales
df_monitor = cargar_datos("data/especies_en_peligro.csv")
especies_monitor = df_monitor.columns.tolist()
info_especies = pd.read_csv("data/info_especies.csv")

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)