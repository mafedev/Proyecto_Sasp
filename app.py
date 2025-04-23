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
from modelo import predecir_nn #Funciones de modelo.py para predecir la probabilidad de extinción usando una red neuronal

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

@app.route("/huella_carbono", methods=["GET", "POST"]) # El get y post es para que la página pueda recibir datos del formulario
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
@app.route("/monitorizar", methods=["GET", "POST"]) # Get y post para 
def monitorizar():
    especie_seleccionada = request.form.get("especie") or especies_monitor[0] # Si no se selecciona ninguna especie, se toma la primera de la lista
    cards = info_especies.to_dict(orient="records") # Se convierte el DataFrame de información de especies a una lista de diccionarios, cada diccionario es una fila

    # Se devuelve la plantilla monitorizar.html con la información de las especies, la especie seleccionada, el año de predicción, el gráfico y el mapa, para poder mostrarlo
    return render_template("monitorizar.html",
                           especies=cards,
                           especie=especie_seleccionada,)

# Ruta para la página de estadísticas de una especie específica, se muestra al seleccionar una especie en monitorizar
@app.route("/estadisticas/<nombre>", methods=["GET", "POST"])  # Se define la ruta con el nombre de la especie como parámetro
def estadisticas(nombre):
    datos_especie = cargar_datos_especie(nombre)  # Se carga la información de la especie desde el archivo CSV
    if not datos_especie:  # Si no se encuentra la especie, muestra un mensaje de error
        return "Especie no encontrada", 404

    metodo = request.form.get("metodo", "lineal")  # Se obtiene el método de predicción seleccionado (lineal o red neuronal), por defecto es lineal
    
    # Se incializan por si no se obtiene un resultado válido
    anio_pred = None
    grafico_b64 = None
    probabilidad_nn = None
    reubicacion = None 

    poblacion_historica = []  # Inicializa la lista de población histórica
    if nombre in df_monitor.columns:  # Verifica si la especie está en el DataFrame, si está significa que tiene datos históricos
        especie_serie = df_monitor[nombre].dropna() # Elimina los valores nulos con dropna()
        poblacion_historica = list(zip(especie_serie.index, especie_serie.values)) # Crea una lista de tuplas con el año y la población, para mostrar en la plantilla

    tendencia_reciente = verificar_tendencia_reciente(df_monitor, nombre) # Verifica la tendencia reciente de la pobalción
    
    # Si el método seleccionado es lineal, se llama a la función de predicción de año de extinción
    if metodo == "lineal":
        anio_pred, grafico_b64 = predecir_anio_extincion(df_monitor, nombre)
        # Si la tendencia es decreciente, obteniene la información de reubicación
        if tendencia_reciente == "Decremento":
            reubicacion = datos_especie.get("reubicacion", "No hay recomendaciones de reubicación disponibles")
    elif metodo == "red_neuronal":  # Si el método seleccionado es red neuronal, se llama a la función de predicción de la red neuronal
        probabilidad_nn = predecir_nn(nombre)  # Se obtiene la probabilidad de extinción de la especie

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
                           anio_pred=anio_pred,
                           acciones_recomendadas=datos_especie.get("acciones_recomendadas"),
                           organizaciones=datos_especie.get("organizaciones"),
                           tendencia_reciente=tendencia_reciente,
                           metodo=metodo,
                           probabilidad_nn=probabilidad_nn,
                           reubicacion=reubicacion)

# FUNCIONES
# Carga la información del archivo CSV
def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    df.set_index("Año", inplace=True) # Establece la columna "Año" como índice del DataFrame
    return df

# Cargar datos iniciales
df_monitor = cargar_datos("data/especies_en_peligro.csv") # Carga el archivo CSV de especies en peligro y lo convierte a un DataFrame
especies_monitor = df_monitor.columns.tolist() # Obtiene los nombres
info_especies = pd.read_csv("data/info_especies.csv")  # Cara el CSV con la información de las especies

# Carga los datos de las especies en peligro de extinción
def cargar_datos_especie(nombre_especie):
    with open('data/info_especies.csv', encoding='utf-8') as archivo_csv: # Abre el archivo CSV con codificación UTF-8, y lo cierra automáticamente al salir del bloque
        diccionario = csv.DictReader(archivo_csv)
        
        for fila in diccionario: # Itera sobre cada fila
            if fila['nombre'] == nombre_especie: # Si el nombre de la especie coincide con el nombre de la fila
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

# Busca el nombre de la especie en la API de GBIF
def buscar_en_gbif(nombre_especie):
    # Primero intenta buscar el nombre completo usando el parámetro `q` para coincidencias amplias
    nombre_especie_codificado = urllib.parse.quote(nombre_especie)
    url = f"https://api.gbif.org/v1/occurrence/search?q={nombre_especie_codificado}&limit=50"
    r = requests.get(url)

    # Verifica si la respuesta es exitosa (código 200)
    if r.status_code == 200:
        resultados = r.json().get("results", []) # Obtiene los resultados de la respuesta JSON
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

# Función para crear un mapa HTML con las observaciones de la especie
def crear_mapa_html(observaciones):
    mapa = folium.Map(location=[0, 0], zoom_start=3)
    for observacion in observaciones: # Cada observación tiene datos como latitud, longitud y país
        lat = observacion.get("decimalLatitude")
        lon = observacion.get("decimalLongitude")
        # Si hay coordenadas, se añade un marcador en el mapa
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"País: {observacion.get('country', 'Desconocido')}"
            ).add_to(mapa)
    return mapa._repr_html_() # Devuelve el mapa en código HTML

# Función para predecir el año de extinción usando regresión lineal
def predecir_anio_extincion(df, especie): # Se le pasa el DataFrame y la especie seleccionada
    try:
        anios = df.index.values.astype(float) # Se obtienen los años del índice del DataFrame y se convierten a float
        poblacion = pd.to_numeric(df[especie], errors="coerce").values # Obtiene los datos de la población y los convierte en números

        # Quita los valores NaN
        datos_validos = ~np.isnan(poblacion)
        anios = anios[datos_validos]
        poblacion = poblacion[datos_validos]

        # Si no hay suficientes años, no se puede hacer la predicción
        if len(anios) < 2:
            return None, None

        # Calculo de la regresión lineal

        promedio_anios = np.mean(anios) # Media de todos los años
        promedio_poblacion = np.mean(poblacion) # Media de todas las poblaciones
        covarianza = np.sum((anios - promedio_anios) * (poblacion - promedio_poblacion))
        varianza = np.sum((anios - promedio_anios) ** 2)

        # Si todos los valores son iguales, no se puede predecir el año
        if varianza == 0:
            return None, None

        # Se calcula la pendiente y el intercepto
        pendiente = covarianza / varianza
        intercepto = promedio_poblacion - pendiente * promedio_anios

        # 
        if pendiente == 0:
            return None, None

        # Se calcula el año de extinción
        anio_extincion = -intercepto / pendiente # Es la formula de la recta y = mx + b

        # GRÁFICA
        # Se crea la gráfica de dispersión y la línea de tendencia
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(anios, poblacion, color='orange', label=especie) # Dibuja los puntos
        poblacion_estim = pendiente * anios + intercepto # Calcula la recta con la formula de la recta
        ax.plot(anios, poblacion_estim, linestyle="--", color="blue", label="Tendencia") # Dibuja la recta
        ax.legend() # Añade la leyenda
        # Etiquetas de los ejes
        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.grid() # Cuadrícula

        buffer = BytesIO() # Crea un buffer para guardar la imagen
        fig.savefig(buffer, format="png") # Guarda la imagen en el buffer
        buffer.seek(0) # Mueve el puntero al inicio del buffer
        imagen_base64 = base64.b64encode(buffer.read()).decode("utf-8") # Codifica la imagen en base64
        plt.close(fig) # Cierra la imagen

        return int(anio_extincion) if anio_extincion > 0 else None, imagen_base64 # Devuelve el año de extinción y la imagen

    except Exception as error: 
        print(f"Error en predecir_anio_extincion: {error}")
        return None, None

# Función para verificar la tendencia reciente de la población de una especie
def verificar_tendencia_reciente(df, especie):
    try:
        datos = df[especie].astype(float).dropna() # Igual que antes, lo convierte a float

        if len(datos) < 10:
            return "No hay suficientes datos para evaluar 10 años"

        # Se toman los últimos 10 años
        ultimos = datos[-10:]

        # Se crean valores ficticios para hacer el cálculo
        x = np.arange(len(ultimos))
        y = ultimos.values

        # Calcular regresión lineal manual
        prom_x = np.mean(x) # Media de los años
        prom_y = np.mean(y) # Media de la población
        covarianza = np.sum((x - prom_x) * (y - prom_y)) # Covarianza entre los años y la población
        varianza = np.sum((x - prom_x) ** 2) # Varianza de los años
        pendiente = covarianza / varianza if varianza != 0 else 0 # Si la varianza es 0, la pendiente es 0

        # Evaluar la tendencia
        if pendiente > 0:
            return "Incremento"
        elif pendiente < 0:
            return "Decremento"
        else:
            return "Estable"

    except:
        return "Error en los datos"

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)